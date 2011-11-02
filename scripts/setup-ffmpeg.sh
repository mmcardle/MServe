#!/bin/bash
########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-10-14
#	Created for Project :		POSTMARK
#
########################################################################


###################################
# report fault and exit function
f_ () {
	printf "\033[01;31m\nMSERVE setup %s\n\n" "$1"
	tput sgr0
	exit 2
}


#######################
# install ffmpeg and update to latest
install_ffmpeg () {
    cd
    apt-get -y update

    # To get presets (.ff presets)
    apt-get -y install ffmpeg

    apt-get -y install build-essential git-core checkinstall yasm texi2html libfaac-dev \
        libopencore-amrnb-dev libopencore-amrwb-dev libsdl1.2-dev libtheora-dev \
        libvorbis-dev libx11-dev libxfixes-dev libxvidcore-dev zlib1g-dev || f_ "failed to install ffmpeg prereqs"

    git clone git://git.videolan.org/x264 || f_ "failed to checkout x264"
    cd x264
    git checkout origin/stable
    ./configure --enable-static || f_ "failed to configure x264"
    make || f_ "failed to make x264"
    checkinstall --pkgname=x264 --default --pkgversion="3:$(./version.sh | \
        awk -F'[" ]' '/POINT/{print $4"+git"$5}')" --backup=no --deldoc=yes || f_ "failed to install x264"

    apt-get -y remove libmp3lame-dev
    apt-get -y install nasm
    cd
    wget http://downloads.sourceforge.net/project/lame/lame/3.98.4/lame-3.98.4.tar.gz || f_ "failed to wget lame"
    tar xzvf lame-3.98.4.tar.gz || f_ "failed to untar lame"
    cd lame-3.98.4
    ./configure --enable-nasm --disable-shared || f_ "failed to configure lame"
    make || f_ "failed to make lame"
    checkinstall --pkgname=lame-ffmpeg --pkgversion="3.98.4" --backup=no --default \
        --deldoc=yes || f_ "failed to install lame"

    cd
    git clone git://git.videolan.org/ffmpeg || f_ "failed to git clone ffmpeg"
    cd ffmpeg
    git checkout n0.8.5
    ./configure --enable-gpl --enable-version3 --enable-nonfree --enable-postproc \
        --enable-libfaac --enable-libopencore-amrnb --enable-libopencore-amrwb \
        --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid \
        --enable-x11grab --enable-libmp3lame || f_ "failed to configure ffmpeg"
    make || f_ "failed to make ffmpeg"
    checkinstall --pkgname=ffmpeg --pkgversion="5:$(./version.sh)" --backup=no \
        --deldoc=yes --default || f_ "failed to install ffmpeg"
    hash x264 ffmpeg ffplay ffprobe
    make tools/qt-faststart || f_ "failed to make qt-faststart"
    checkinstall --pkgname=qt-faststart --pkgversion="$(./version.sh)" --backup=no \
        --deldoc=yes --default install -D -m755 tools/qt-faststart /usr/local/bin/qt-faststart || f_ "failed to install qt-faststart"

    # Copy Presets
    cp  /usr/share/ffmpeg/* /usr/local/share/ffmpeg/ || f_ "failed to copy ffmpeg presets"
}

install_ffmpeg || f_ "failed to install ffmpeg"