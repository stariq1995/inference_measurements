reset
set autoscale
set datafile separator ","
set title "Face detection processing over time"
set xlabel "Time(seconds)"
set ylabel "Frames Per Second"
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 1,0.9
set output "timeseries.eps"
plot "timeseries.txt" using 1:2 title col with lines
#set terminal png size 2560,1920 enhanced font 'NimbusSanL-Regu' 14
#set output "../plot_outputs/fig_faces-V-time_feat-3.png"
#replot