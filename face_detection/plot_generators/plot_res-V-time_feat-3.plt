reset
set autoscale
set title "Full Face Feature Detection times for different image sizes"
set xlabel "Size(MB)"
set ylabel "Time(s)"
set terminal postscript eps color enhanced 'NimbusSanL-Regu' 14
set size 1,0.9
set output "../plot_outputs/fig_res-V-time_feat-3.eps"
plot "../raw_data/output_res-V-time_feat-3.txt" using 1:2 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-3.txt" using 1:3 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-3.txt" using 1:4 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-3.txt" using 1:5 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-3.txt" using 1:6 title col with linespoints, \
	"../raw_data/output_res-V-time_feat-3.txt" using 1:7 title col with linespoints
#set terminal png size 2560,1920 enhanced font 'NimbusSanL-Regu' 14
#set output "../plot_outputs/fig_faces-V-time_feat-3.png"
#replot