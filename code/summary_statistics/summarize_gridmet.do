clear
cd /pool001/vilgalys/inferring_expectations/


// First column: all weather variables, in all service areas, from 2013-2021 

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 

eststo clear 

local var_list  tmmx tmmn pr sph vs th vpd rmax rmin srad bi erc pet etr fm100 fm1000 elevation 

replace tmmn = tmmn-273.15
replace tmmx = tmmx-273.15

label var sph "Specific Humidity (kg/kg)"
label var vpd "Mean Vapor Pressure Deficit (kPa)"
label var pr "Precipitation Amount (daily mm)"
label var rmin "Min Relatively Humidity (\%)"
label var rmax "Max Relatively Humidity (\%)"
label var srad "Surface Downwelling Shortwave Flux (W/m$^2$)"
label var tmmn "Min Air Temperature (C)"
label var tmmx "Max Air Temperature (C)"
label var vs "Wind Velocity at 10 m (m/s)"
label var th "Wind From Direction (Degrees past North)"
label var pet "Potential Evapotranspiration (Derived, mm)"
label var etr "Reference Evapotranspiration (Derived, mm)"
label var fm100 "Dead Fuel Moisture 100 hr (Derived, \%)"
label var fm1000 "Dead Fuel Moisture 1000 hr (Derived, \%)"
label var bi "Burning Index (Derived)"
label var erc "Energy Release Component (Derived)"
label var elevation "Elevation"

foreach y in "all" "red_flag" "psps" {
    eststo grp_`y': estpost summ `var_list' [aweight=length] if `y'==1
}


esttab grp* using "/pool001/vilgalys/inferring_expectations/outputs/summary_stats/gridmet_summary_table.tex", main(mean) aux(sd) nostar unstack nonote label collabels(none) eqlabels("All Circuits" "Red Flag Warnings" "During PSPS Days") nomtitles varwidth(45) replace

esttab grp* , wide main(mean) aux(sd) nostar unstack nonote label eqlabels("All Circuits" "Red Flag Warnings" "During PSPS Days") nomtitles varwidth(45)