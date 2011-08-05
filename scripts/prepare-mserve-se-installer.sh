#! /bin/bash

#prepare release installer

# assume binary

if [ $# -ne 1 ]; then
	echo "Usaage: $0  <template_script>"
	exit 1
fi

template=$1
payload=$2
target="mserve_setup_installer.sh"

#check template exists
if [ ! -f "$template" ]; then
	echo "cannot find template script $template"
	exit 1
fi

echo "create temporary directory"
mkdir tmp-$$
cd tmp-$$
echo "get mserve from repository"
mserve_url="git://soave.it-innovation.soton.ac.uk/git/pp-dataservice"
git clone $mserve_url
cd pp-dataservice
git submodule init 
git submodule update
cd ..

mkdir mserve
cp -ar pp-dataservice/mserve/* mserve
cp -ar pp-dataservice/{scripts,static,README.txt} mserve
tar cvfz mserve.tgz mserve
cd ..

#cp "$template" mserve_installer
sed -e "s#^MSERVE_ARCHIVE=NOTSET\$#MSERVE_ARCHIVE=_mserve.tgz#" \
	"$template" > "$target"

echo "PAYLOAD:" >> "$target"
cat tmp-$$/mserve.tgz >> "$target"

rm -rf tmp-$$
chmod +x $target
echo -e "\n\nMSERVE self-extracted installer $target has been successfully created."
