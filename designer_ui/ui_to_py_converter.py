import os

path_designer_uis = './designer_ui/'
ui_files = [file for file in os.listdir('./designer_ui/') if file.endswith('.ui')]
for ui_file in ui_files:
    os.system(f'pyuic6 {os.path.join(path_designer_uis, ui_file)} -o ./ui/{ui_file.replace(".ui", ".py")}')