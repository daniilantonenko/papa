from nicegui import ui, binding
from parser import scan_all, save_to_database, get_soup
import asyncio
import json
from utils import fetch_response, find_html, extract_chars, download_file

# Создание страницы админ-панели
def content() -> None:
    ui.page_title('Админ-панель')

    async def perform_scan():
        result = 0
        
        try:
            print("Scanning...")
            task = asyncio.create_task(scan_all())
            result = await task
        except Exception as e:
            print(f"Error: {e}")
            ui.notify(f'Сканирование завершено с ошибками')

        print("Scan completed")
        ui.notify(f'Сканирование завершено, изменилось {result} страниц')

    try:
        with open('data.json', 'r') as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    except FileNotFoundError:
        return

    async def get_config_json(editor: ui.json_editor):
        new_config = await editor.run_editor_method('get')
        
        if 'text' in new_config:
            new_config = new_config['text']
            try:
                new_config = json.loads(new_config)
            except json.JSONDecodeError:
                ui.notify('Некорректная конфигурация json')
                return
        elif 'json' in new_config:
            new_config = new_config['json']
        else:
            ui.notify('Некорректная конфигурация json_editor')
            return

        return new_config

    async def save_config():
        nonlocal json_editor
        new_config = await get_config_json(json_editor)
        
        try:
            with open('data.json', 'w') as f:
                json.dump(new_config, f,ensure_ascii=False,indent=4)
        except Exception as e:
            ui.notify(f'Error saving config: {e}')

        try:
            await save_to_database(new_config)
        except Exception as e:
            ui.notify(f'Error saving to database: {e}')
        
        ui.notify('Конфигурация сохранена')

    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    class Search:
        value = binding.BindableProperty()
        url = binding.BindableProperty()
        org = binding.BindableProperty()
        proffile_list = binding.BindableProperty()

        def __init__(self):
            self.url = ''
            self.org = ''
            self.proffile_list = ''
            self.html = ''

        async def soup_string(self,cfg):
            """
            Get the HTML response for the given URL and update...

            If the response is not 200, return None.
            """
            #Get the response
            response = await fetch_response(self.url)
            if response is None:
                return
            #Get the soup
            soup = get_soup(response.text)

            #Get the proffiles
            self.proffile_list = []
            chats_table, chars_name, chars_value, disable_chars = None, None, None, None
            list_proffiles = {org['name']: [proffile for proffile in org['Proffile']] for org in cfg}
            domain = next((org.get('domain') for org in cfg if org.get('name') == self.org), None)          
            p_list = [proffile for proffile in list_proffiles[self.org]]
            for proffile in p_list:
                proffile_attrdict = AttrDict()
                proffile_attrdict.update({
                    **proffile,
                })
                if proffile_attrdict['name'] == 'characteristics_table':
                    chats_table = proffile_attrdict
                elif proffile_attrdict['name'] == 'characteristics_name':
                    chars_name = proffile_attrdict
                    disable_chars = proffile_attrdict.get('disable', False)
                elif proffile_attrdict['name'] == 'characteristics_value':
                    chars_value = proffile_attrdict
                else:
                    self.proffile_list.append(find_html(proffile_attrdict,soup))
            
            if chats_table and chars_name and chars_value:
                chars = extract_chars(soup, chats_table, chars_name, chars_value)
                if chars is not None:
                    chars_str = ''.join(f'{key}: {value}<br>' if key not in disable_chars else '' for key, value in chars.items())
                    self.proffile_list.append(chars_str)

            self.html = ''
            for data in self.proffile_list:
                # Check if the proffile is an image
                allow_filetype = ('.jpg', '.png')
                if data is not None and isinstance(data, str) and data.endswith((allow_filetype)):
                    url = data if data.startswith(('http://', 'https://', '//')) else domain + data
                    file_path = await download_file(url, 'cache/')
                    if file_path is not None:
                        self.html += '<div><img src="' + file_path + '"></div><br>'
                    else:
                        print("image is none")
                        continue
                elif data is not None and isinstance(data, str):
                        self.html += '<div>' + data + '</div><br>'
                else:
                    self.html += '<div>None</div><br>'
    
    class AsyncButton(ui.button):
        def __init__(self, *args, onclick_async=None, **kwargs):
            with ui.row():
                super().__init__(*args, **kwargs)
                self.spinner = ui.spinner(size='2em').classes('m-1')
                self.spinner.visible = False
            self.on_click(self.async_click)
            self.onclick_async = onclick_async 

        async def async_click(self):
            self.spinner.visible = True
            self.disable()  # Disable the button
            try:
                if callable(self.onclick_async):
                    await self.onclick_async()
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.spinner.visible = False
                self.enable()  # Enable the button

    # Create the UI
    with ui.header().classes('items-center justify-between q-pa-sm'):
        ui.button('Главная', icon='home').props('flat color=white').on_click(lambda: ui.navigate.to('/'))
        with ui.row():
            ui.button('Каталог', icon='store').props('flat color=white').on_click(lambda: ui.navigate.to('/admin/catalog'))
        ui.button('Админ-панель', icon='settings').props('flat color=white').on_click(lambda: ui.navigate.to('/admin'))

    json_editor = ui.json_editor({'content': {'json': config }})
    
    async def update_config():
            nonlocal config
            config = await get_config_json(json_editor)

    json_editor.on_change(update_config)

    with ui.right_drawer(fixed=False).props('bordered'):
        ui.label('Исследовать').classes('font-bold')
        soup = Search()
        
        list_orgs = [org['name'] for org in config['Organization']]

        research_organization = ui.select(options=list_orgs, label='Организация',value=list_orgs[0]).bind_value(soup, 'org').classes('w-full')
        research_url = ui.input('URL').bind_value(soup, 'url').classes('w-full')
        async def super_scan():
            await soup.soup_string(config['Organization'])
        superscan_btn = AsyncButton('Сканировать', onclick_async=super_scan).props('outline')

        ui.html('').bind_content(soup, 'html').classes('w-full')
        

    with ui.footer().style('background-color: #eeeeee'):
        with ui.row():
            AsyncButton('Сохранить', onclick_async=save_config)
            AsyncButton('Сканировать', onclick_async=perform_scan).props('outline')
            spinner = ui.spinner(size='2em').classes('m-1')
            spinner.visible = False
            #TODO: Add progress bar
            


class PageExpansion:
    def __init__(self, container) -> None:
        self.container = container
    
    def add(self, org=None):
        with self.container:
            i = self.count_row(self.container)
            #name = f"{org["name"]}"
            with ui.expansion(text=f'{org["name"]}' if org else "New oranisation", caption=f'{org["domain"]}' if org else "domain", icon='work').classes('w-full') as row:
                self.org_content(org)
                ui.button('Удалить', on_click=lambda: self.container.remove(row))
    
    def count_row(self, element):
        return len(list(element)) 
    
    def org_content(self, organization):
        with ui.column().classes('w-full') as org:
            
            ui.label('Профили')
            if not organization:
                pass
            
            profiles = organization.get('Proffile', [])
            
            
            def add_profile():
                pass
            
            if len(profiles) == 0:
                add_profile()
            else:
                rows = [{'name': profile.get('name', ''), 'tag': profile.get('tag', ''), 
                'attribute': profile.get('attribute', ''), 'value': profile.get('value', ''), 
                'template': profile.get('template', ''), 'value_attribute': profile.get('value_attribute', '')} 
                for profile in organization.get('Proffile', [])]
                
                def handle_cell_value_change(e):
                    new_row = e.args['data']
                    ui.notify(f'Updated row to: {e.args["data"]}')
                    rows[:] = [row | new_row if row['id'] == new_row['id'] else row for row in rows]
                    
                aggrid = ui.aggrid({
                    'rowData': rows,
                    'columnDefs': [
                        {'field': 'name', 'headerName': 'Имя', 'editable': True},
                        {'field': 'tag', 'headerName': 'Тег', 'editable': True},
                        {'field': 'attribute', 'headerName': 'Атрибут', 'editable': True},
                        {'field': 'value', 'headerName': 'Значение', 'editable': True},
                        {'field': 'template', 'headerName': 'Шаблон', 'editable': True},
                        {'field': 'value_attribute', 'headerName': 'Атрибут значения', 'editable': True}
                    ],
                    'rowSelection': 'multiple',
                    'stopEditingWhenCellsLoseFocus': True,
                }).on('cellValueChanged', handle_cell_value_change)

            ui.button('Добавить профиль', on_click=add_profile)

            ui.label('URLs')
            urls = organization.get('Urls', [])
            
            def add_url():
                pass
            
            if len(urls) == 0:
                add_url()
            else:
                urls_table = [{'url': url} for url in urls]
                ui.table(rows=urls_table)

            ui.button('Добавить URL', on_click=add_url)
        return
    
    def add_button(self):
        ui.button('Добавить', on_click=lambda: self.add())
    
    def clear_button(self):
        ui.button('Очистить', on_click=self.container.clear)