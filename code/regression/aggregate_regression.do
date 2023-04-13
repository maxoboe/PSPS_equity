clear
cd /pool001/vilgalys/inferring_expectations/
log using ~/aggregate_regression.log, replace
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

label var sens "Health Index"
label var socio "SES Index"

local community_vars sens socio
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

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_psps_logistic_regression.tex", se keep(sens socio) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_psps_logistic_regression.csv", replace wide plain se keep(sens socio) pr2 scalars(Population Primary Derived) 


use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)

keep if has_year_utility
eststo clear 

label var Utility "Utility"

encode Utility, gen(utility)

label var sens "Health Index"
label var socio "SES Index"

local community_vars sens socio
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

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_psps_logistic_regression_full_sample.tex", se keep(sens socio) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar

esttab using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_psps_logistic_regression_full_sample.csv", replace wide plain se keep(sens socio) pr2 scalars(Population Primary Derived) 


* Switching to CMI regression 
use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
eststo clear 

keep if psps
gen log_customers = log(TOTAL_CUST)
gen log_duration = log(Outage_Hou)
gen log_CMI = log(CMI)
gen log_Pop = log(TotPop19)

label var socio "SES Index"
label var sens "Health Index"

local community_vars sens socio
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.log_Pop
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

label var log_customers "Log Cust"
label var log_duration "Log Dur"
label var log_CMI "Log CMI"
label var Utility "Utility"

encode Utility, gen(utility)

reg log_customers `community_var_list', robust
eststo customers_community_

reg log_customers `population_var_list', robust
eststo customers_population_
estadd loc Population "X"


// Using primary weather vars 
reg log_customers `primary_var_list', robust

eststo customers_primary_
estadd loc Population "X"
estadd loc Primary "X"

reg log_customers `all_var_list', robust

eststo customers_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

esttab customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_customers_regression.tex", se keep(sens socio) r2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nodepvar
esttab customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_customers_regression.csv", replace wide plain se  keep(sens socio) r2 scalars(Population Primary Derived) 


reg log_CMI `community_var_list', robust
eststo CMI_community_

reg log_CMI `population_var_list', robust
eststo CMI_population_
estadd loc Population "X"


// Using primary weather vars 
reg log_CMI `primary_var_list', robust

eststo CMI_primary_
estadd loc Population "X"
estadd loc Primary "X"

reg log_CMI `all_var_list', robust

eststo CMI_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

esttab CMI* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_CMI_regression.tex", se keep(sens socio) r2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nodepvar
esttab CMI* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_CMI_regression.csv", replace wide plain se  keep(sens socio) r2 scalars(Population Primary Derived) 

esttab CMI* customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_CMI_customers_regression.tex", se keep(sens socio) r2 scalars(Population Primary Derived) label collabels(none) replace

// First column: all weather variables, in all service areas, from 2014-2021 

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"

keep if shutoff_flag

eststo clear 

label var Utility "Utility"

encode Utility, gen(utility)

local community_vars sens socio 
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.log_Pop
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

logit ignition `community_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_community_

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_community, replace 
drop phat ihat error lb ub plb pub 

logit ignition `population_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_population_
estadd loc Population "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_population, replace 
drop phat ihat error lb ub plb pub 

logit ignition `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_primary_
estadd loc Population "X"
estadd loc Primary "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_primary, replace 
drop phat ihat error lb ub plb pub 

logit ignition `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_all, replace 
drop phat ihat error lb ub plb pub 

esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition.tex, se keep(socio sens) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition.csv, replace wide plain se keep(socio sens) pr2 scalars(Population Primary Derived)

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"
eststo clear 

encode Utility, gen(utility)

local community_vars sens socio 
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.log_Pop
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

logit ignition `community_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_community_

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_community_full_sample, replace 
drop phat ihat error lb ub plb pub 

logit ignition `population_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_population_
estadd loc Population "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_population_full_sample, replace 
drop phat ihat error lb ub plb pub 

logit ignition `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_primary_
estadd loc Population "X"
estadd loc Primary "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_primary_full_sample, replace 
drop phat ihat error lb ub plb pub 

logit ignition `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_all_full_sample, replace 
drop phat ihat error lb ub plb pub 

esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition_full_sample.tex, se keep(socio sens) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition_full_sample.csv, replace wide plain se keep(socio sens) pr2 scalars(Population Primary Derived)

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"
gen ignition_or_psps = ignition==1 | psps==1
label var ignition_or_psps "ignition"
eststo clear 

encode Utility, gen(utility)

local community_vars sens socio 
local community_var_list  `community_vars' i.year_x#i.utility
local population_var_list  `community_var_list' i.year_x#i.utility#c.log_Pop
local primary_var_list `population_var_list' i.year_x#i.utility#c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x#i.utility#c.(bi erc pet etr fm100 fm1000)

logit ignition_or_psps `community_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_community_

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_community_psps_1, replace 
drop phat ihat error lb ub plb pub 

logit ignition_or_psps `population_var_list', vce(robust)
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_population_
estadd loc Population "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_population_psps_1, replace 
drop phat ihat error lb ub plb pub 

logit ignition_or_psps `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_primary_
estadd loc Population "X"
estadd loc Primary "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_primary_psps_1, replace 
drop phat ihat error lb ub plb pub 

logit ignition_or_psps `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
predict phat
predict ihat, xb
predict error, stdp
generate lb = ihat - invnormal(0.975)*error
generate ub = ihat + invnormal(0.975)*error
generate plb = invlogit(lb)
generate pub = invlogit(ub)
eststo ignition_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

save /nobackup1/vilgalys/data/ignition_prob/aggregate_linear_all_psps_1, replace 
drop phat ihat error lb ub plb pub 

esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition_psps_1.tex, se keep(socio sens) pr2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
esttab ignition* using /pool001/vilgalys/inferring_expectations/outputs/regressions/aggregate_logistic_regression_ignition_psps_1.csv, replace wide plain se keep(socio sens) pr2 scalars(Population Primary Derived)

log close
