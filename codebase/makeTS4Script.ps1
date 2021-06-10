$FileName = "riv_rel"

# Delete the folder and ts4script if it already exists
Remove-Item ./__pycache__ -Recurse -ErrorAction Ignore
Remove-Item ./$FileName.ts4script -Recurse -ErrorAction Ignore

# Compile Everything
python -m compileall .

# Remove the .cpython-37
ls ./__pycache__ | Rename-Item -NewName {$_.name -replace ".cpython-37",""}

# Put everything inside the zip file
ls ./__pycache__ | ForEach-Object {
	Compress-Archive ./__pycache__/$_ ($FileName + ".zip")
}

# Rename the zip to a ts4script
Rename-Item -Path ($FileName+".zip") -NewName ($FileName+".ts4script")