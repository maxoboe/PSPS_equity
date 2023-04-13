
clear
cd /nobackup1/vilgalys/
set maxvar 32767
set matsize 11000


// First column: all weather variables, in all service areas, from 2014-2021 

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
keep if psps
gen log_Pop = log(TotPop19)
gen more_than_24 = cond(Outage_Hou >=24, 1, 0)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Risk Index"
label var more_than_24 "Duration > 24 Hours"


foreach utility in "SCE" "PG&E" "SDG&E" {
    foreach binary in 0 1 {
        local _label: subinstr local utility  "&" ""
        eststo `_label'_`binary': estpost summ sens socio if (more_than_24 == `binary') & (Utility == "`utility'")
        estadd loc Utility `_label' 
        if `binary' == 1 {
            estadd loc "geq24" "X"
        }
        estadd matrix se =  e(sd) / sqrt(e(N))
        * display e(sd)
        * estadd se = e(sd) / sqrt(e(N))
    }
}

esttab, main(mean) aux(se) scalars("Utility Utility" "geq24 \(\geq\) 24 Hours") label
esttab using /pool001/vilgalys/inferring_expectations/outputs/summary_stats/duration_geq_24.tex, main(mean) aux(se) scalars("Utility Utility" "geq24 \geq 24 Hours") label