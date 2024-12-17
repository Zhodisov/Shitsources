from pathlib import Path
from reader import Parser
from typing import Dict, Optional
import aiofiles, aiohttp, asyncio, cryptjson, gui, keys, os, shutil, subprocess

class Client:

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop]=None):
        self.download_main_data = False
        self.main_data = None
        self.swf_data = None
        self.loop = loop or asyncio.get_event_loop()
        self.parser_task = None
        self.access_token = ''
        self.level = ''

    async def connect(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://tfmdisney.herokuapp.com/auth', params={'key':keys.client_vip_id, 
                 'version':keys.client_version}) as response:
                    data = await response.json()
                    if response.status == 200:
                        self.access_token = data.pop('access_token', '')
                        if self.access_token:
                            self.loop.create_task(self.start(data))
                        else:
                            gui.app.show_info('Internal server error. Try again later', mode='error')
                    elif response.status == 401:
                        gui.app.show_info('Invalid key', mode='error')
                        shutil.rmtree((keys.data_path), ignore_errors=True)
                    else:
                        if response.status == 406:
                            gui.app.show_info("There's a new update available. Press Yes to download", mode='askupdate',
                              url=(data.pop('update_url', '')),
                              destroy=True)
                            shutil.rmtree((keys.data_path), ignore_errors=True)
        except aiohttp.client_exceptions.ClientConnectorError:
            gui.app.show_info('Connection error. Try again', mode='error')

    async def start(self, data: Dict):
        self.level = data.pop('level', '')
        if os.path.isdir(keys.data_path):
            if not os.listdir(keys.data_path):
                self.download_main_data = True
            elif os.path.isfile(keys.version_file):
                async with aiofiles.open(keys.version_file, 'r+') as f:
                    content = await f.read()
                    if keys.client_version != content:
                        self.download_main_data = True
            else:
                self.download_main_data = True
        else:
            Path(keys.data_path).mkdir(parents=True, exist_ok=True)
            self.download_main_data = True
        if data.pop('update_data', False):
            self.download_main_data = True
        async with aiofiles.open(keys.version_file, 'w+') as f:
            await f.write(keys.client_version)
        gui.app.is_next_frame = True
        gui.app.create_widgets()
        gui.app.update_log_text('Connected.')

    async def load_data(self, data_type: str, data: Optional[str]=None):
        if data is not None:
            if data_type == 'main':
                self.main_data = cryptjson.json_unzip(data)

                async def write_files(obj, file):
                    if isinstance(obj, str):
                        async with aiofiles.open(file, 'w+b') as f:
                            await f.write(bytearray(cryptjson.text_decode(obj)))
                    else:
                        if not os.path.isdir(file):
                            os.mkdir(file)
                        for key, val in obj.items():
                            await write_files(val, os.path.join(file, key))

                for key, val in self.main_data.items():
                    file_path = os.path.join(keys.data_path, key)
                    if isinstance(val, str):
                        async with aiofiles.open(file_path, 'w+b') as f:
                            await f.write(bytearray(cryptjson.text_decode(val)))
                else:
                    if not os.path.isdir(file_path):
                        os.mkdir(file_path)
                    for inner_key, inner_val in val.items():
                        await write_files(inner_val, os.path.join(file_path, inner_key))

            else:
                if data_type == 'swf':
                    self.swf_data = cryptjson.json_unzip(data)
                    while True:
                        self.parser_task = self.loop.create_task(self.parse_data())
                        if gui.app.check_btn_var3.get() == 0:
                            break
                        await self.parser_task
                        await asyncio.sleep(180)
                        gui.app.update_log_text(clear=True)

    async def parse_data(self):
        if self.swf_data is None:
            gui.app.update_log_text('Downloading data...')
            data_type = 'swf'
            if self.download_main_data:
                data_type += '-main'
            async with aiohttp.ClientSession() as session:
                async with session.get('https://tfmdisney.herokuapp.com/get_data', params={'access_token':self.access_token, 
                 'data_type':data_type}) as response:
                    if response.status == 200:
                        data = await response.json()
                        await self.load_data('main', data.pop('main_data', None))
                        await self.load_data('swf', data.pop('swf_data', None))
                    else:
                        gui.app.show_info('Request error. Try again later', mode='error')
        else:
            parser = Parser((self.level != ''), (self.swf_data), premium_level=(self.level))
            success = await parser.start()
            if success:
                await parser.update_client_mode(keys.client_mode, keys.load_chargeur)
                await parser.update_chargeur()
                self.end_process()
            else:
                gui.app.update_button['state'] = 'normal'
                gui.app.update_log_text('An error has occurred. Try again')

    def end_process(self):
        chargeur_main_path = os.path.join(keys.chargeur_data_path, 'ChargeurTransformice-0.main.asasm')
        chargeur_main_abc = os.path.join(keys.chargeur_data_path, 'ChargeurTransformice-0.main.abc')
        chargeur_swf_path = os.path.join(keys.data_path, 'ChargeurTransformice.swf')
        rabcasm = subprocess.Popen(['tools/rabcasm', chargeur_main_path], shell=False, creationflags=(subprocess.CREATE_NO_WINDOW))
        rabcasm.wait()
        abcrep = subprocess.Popen(['tools/abcreplace', chargeur_swf_path, '0', chargeur_main_abc], shell=False, creationflags=(subprocess.CREATE_NO_WINDOW))
        abcrep.wait()
        if gui.app.check_btn_var2.get() == 1:
            if gui.app.check_btn_var3.get() == 0:
                if os.path.isfile('Adobe.exe'):
                    subprocess.Popen(['Adobe', chargeur_swf_path])
        gui.app.update_button['state'] = 'normal'
        gui.app.update_log_text('Done!')
        if gui.app.check_btn_var.get() == 1:
            gui.app.close()
