FileName=riv_rel_addon_GT

find . -type d -name '__pycache__' -exec rm -r {} +
rm -f ./$FileName.ts4script
rm -f ./$FileName.zip
rm -rf ./compiled
mkdir compiled

python -m compileall .

for path in $(find . -type f -path '*/__pycache__/*' -name '*.pyc'); do
	newpath=$(echo $path | sed s!/__pycache__!! | sed s!\.cpython.*\.pyc!.pyc! | sed s!^.!compiled!)
	mkdir -p "$(dirname $newpath)"
	mv "$path" "$newpath"
done

cd compiled
zip -r $FileName.zip ./*

mv "$FileName.zip" "../$FileName.ts4script"