clear
cd /pool001/vilgalys/inferring_expectations/
set maxvar 32767
set matsize 11000
set maxiter 100


// First column: all weather variables, in all service areas, from 2014-2021 

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)

keep if red_flag
keep if has_year_utility
eststo clear 

label var Utility "Utility"

encode Utility, gen(utility)

gen PGE_sens = cond(Utility == "PG&E", sens, 0)
label var PGE_sens "PG\&E x Health"
gen PGE_socio = cond(Utility == "PG&E", socio, 0)
label var PGE_socio "PG\&E x SES"
gen SCE_sens = cond(Utility == "SCE", sens, 0)
label var SCE_sens "SCE x Health"
gen SCE_socio = cond(Utility == "SCE", socio, 0)
label var SCE_socio "SCE x SES"
gen SDGE_sens = cond(Utility == "SDG&E", sens, 0)
label var SDGE_sens "SDG\&E x Health"
gen SDGE_socio = cond(Utility == "SDG&E", socio, 0)
label var SDGE_socio "SDG\&E x SES"

local community_vars SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.(log_Pop) 
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

eststo clear 


logit psps `community_var_list', vce(robust)

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo community_
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 

drop _predicted tp tn fp fn Specificity Sensitivity

logit psps `population_var_list', vce(robust)

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo population_
estadd loc Population "X"
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 

drop _predicted tp tn fp fn Specificity Sensitivity

// Using primary weather vars 
logit psps `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo primary_
estadd loc Population "X"
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 
estadd loc Primary "X"

drop _predicted tp tn fp fn Specificity Sensitivity


logit psps `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo all_
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

drop _predicted tp tn fp fn Specificity Sensitivity

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/psps_logistic_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/psps_logistic_regression.csv", replace wide plain se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) pr2 scalars(Population Primary Derived) 


use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
keep if has_year_utility
eststo clear 

label var Utility "Utility"

encode Utility, gen(utility)

gen PGE_sens = cond(Utility == "PG&E", sens, 0)
label var PGE_sens "PG\&E x Health"
gen PGE_socio = cond(Utility == "PG&E", socio, 0)
label var PGE_socio "PG\&E x SES"
gen SCE_sens = cond(Utility == "SCE", sens, 0)
label var SCE_sens "SCE x Health"
gen SCE_socio = cond(Utility == "SCE", socio, 0)
label var SCE_socio "SCE x SES"
gen SDGE_sens = cond(Utility == "SDG&E", sens, 0)
label var SDGE_sens "SDG\&E x Health"
gen SDGE_socio = cond(Utility == "SDG&E", socio, 0)
label var SDGE_socio "SDG\&E x SES"

local community_vars SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.(log_Pop) 
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

eststo clear 


logit psps `community_var_list', vce(robust)

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo community_
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 

drop _predicted tp tn fp fn Specificity Sensitivity

logit psps `population_var_list', vce(robust)

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo population_
estadd loc Population "X"
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 

drop _predicted tp tn fp fn Specificity Sensitivity

// Using primary weather vars 
logit psps `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo primary_
estadd loc Population "X"
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 
estadd loc Primary "X"

drop _predicted tp tn fp fn Specificity Sensitivity


logit psps `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance

predict _predicted 
replace _predicted = cond(_predicted >= 0.5, 1, 0) 
egen tp = sum(cond(_predicted == 1 & psps == 1, 1, 0))
egen tn = sum(cond(_predicted == 0 & psps == 0, 1, 0))
egen fp = sum(cond(_predicted == 1 & psps == 0, 1, 0))
egen fn = sum(cond(_predicted == 0 & psps == 1, 1, 0))


gen Specificity = tp / (tp + fn)
gen Sensitivity = tn / (tn + fp)
loc sens = Sensitivity 

eststo all_
estadd scalar Sensitivity = Sensitivity 
estadd scalar Specificity = Specificity 
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

drop _predicted tp tn fp fn Specificity Sensitivity

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/psps_logistic_regression_full_sample.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/psps_logistic_regression_full_sample.csv", replace wide plain se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) pr2 scalars(Population Primary Derived) 
