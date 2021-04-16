rm -rf __processing_core
mkdir __processing_core
curl -L https://github.com/processing/processing/releases/download/processing-0270-3.5.4/processing-3.5.4-linux64.tgz>__processing_core/processing.tgz
tar -C __processing_core -xvf __processing_core/processing.tgz --strip-components=1 processing-3.5.4/core/library
cp -f __processing_core/core/library/* __processing_core
rm -f __processing_core/processing.tgz
rm -rf __processing_core/core
