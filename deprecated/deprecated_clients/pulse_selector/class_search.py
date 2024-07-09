import os

root = "/home/qsimexpcontrol/LabRAD/Qsim/scripts/pulse_sequences"

for path, subdirs, files in os.walk(root):
    for name in files:
        if (name[-3:] == '.py') and (name != '__init__.py'):
            import_path = os.path.join(path[len(root) + 1:], name[:-3])
            import_path = import_path.replace('/','.')
            print import_path
            #__import__('Qsim.scripts.pulse_sequences.' + import_path)