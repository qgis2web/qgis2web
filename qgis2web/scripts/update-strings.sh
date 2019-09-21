#!/bin/bash
LOCALES=$*

# Get newest .py files so we don't update strings unnecessarily

CHANGED_FILES=0
PYTHON_FILES=`find . -regex ".*\(ui\|py\)$" -type f`
for PYTHON_FILE in $PYTHON_FILES
do
  CHANGED=$(stat -c %Y $PYTHON_FILE)
  if [ ${CHANGED} -gt ${CHANGED_FILES} ]
  then
    CHANGED_FILES=${CHANGED}
  fi
done

# Qt translation stuff
# for .ts file
UPDATE=false
for LOCALE in ${LOCALES}
do
  TRANSLATION_FILE="i18n/$LOCALE.ts"
  if [ ! -f ${TRANSLATION_FILE} ]
  then
    # Force translation string collection as we have a new language file
    touch ${TRANSLATION_FILE}
    UPDATE=true
    break
  fi

  MODIFICATION_TIME=$(stat -c %Y ${TRANSLATION_FILE})
  if [ ${CHANGED_FILES} -gt ${MODIFICATION_TIME} ]
  then
    # Force translation string collection as a .py file has been updated
    UPDATE=true
    break
  fi
done

if [ ${UPDATE} == true ]
# retrieve all python files
then
  print ${PYTHON_FILES}
  # update .ts
  echo "Please provide translations by editing the translation files below:"
  for LOCALE in ${LOCALES}
  do
    echo "i18n/"${LOCALE}".ts"
    # Note we don't use pylupdate with qt .pro file approach as it is flakey
    # about what is made available.
    pylupdate4 -noobsolete ${PYTHON_FILES} -ts i18n/${LOCALE}.ts
  done
else
  echo "No need to edit any translation files (.ts) because no python files"
  echo "has been updated since the last update translation. "
fi
