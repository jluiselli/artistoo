#!/bin/bash
ffmpeg -y -r 40 -pattern_type glob -i "Mitochondria-fraction_unmutated-t/Mitochondria-fraction_unmutated-t*.png" video_unmut.mp4 > tmpout.txt
ffmpeg -y -r 40 -pattern_type glob -i "Mitochondria-n_DNA-t/Mitochondria-n_DNA-t*.png" video_ndna.mp4 > tmpout.txt
ffmpeg -y -r 40 -pattern_type glob -i "Mitochondria-oxphos_avg-t/Mitochondria-oxphos_avg-t*.png" video_oxphos.mp4 > tmpout.txt
ffmpeg -y -i video_unmut.mp4 -i video_ndna.mp4 -i video_oxphos.mp4 -filter_complex "[1:v][0:v]scale2ref=oh*mdar:ih[1v][0v];[2:v][0v]scale2ref=oh*mdar:ih[2v][0v];[0v][1v][2v]hstack=3,scale='2*trunc(iw/2)':'2*trunc(ih/2)'" -hide_banner -loglevel error -nostdin  video_all.mp4 > tmpout.txt
