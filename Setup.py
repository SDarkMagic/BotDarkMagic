# Sets up the directory to be used for running an appropriate environment for the bot and server

import pathlib
import os

emptyDict = {}
pipFileData = open(pathlib.Path(./'pipfileTemplate.txt'), 'rt')
pipfileTemplate = pipFileData.read()
varPath = pathlib.Path('./Vars')
globablVarFile = pathlib.Path(f'varPath/{globalVars.json}')

def main():
  os.system('pipenv --python 3.7')
  with open ('./Pipfile', 'wt') as writePipfile:
    writePipfile.write(pipfileTemplate)
  os.system('pipenv sync')

  if varPath.exists():
    pass
  else:
    os.mkdir(varPath)
  if globablVarFile.exists():
    pass
  else:
    with open(globablVarFile, 'wt') as writeGlobVars:
      writeGlobVars.write(emptyDict)
  return
  
  if __name__ == '__main__':
    main()