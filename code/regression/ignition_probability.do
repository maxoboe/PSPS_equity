
clear
cd /nobackup1/vilgalys/
set maxvar 32767
set matsize 11000


// First column: all weather variables, in all service areas, from 2014-2021 

use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"

keep if shutoff_flag

eststo clear 

local community_vars sens socio 
local community_var_list  `community_vars' i.year_x
local population_var_list  `community_var_list' i.year_x##c.log_Pop
local primary_var_list `population_var_list' i.year_x##c.(tmmx tmmn pr sph vs th vpd rmax rmin srad elevation)
local all_var_list  `primary_var_list' i.year_x##c.(bi erc pet etr fm100 fm1000)

preserve 

foreach utility in "SCE" "PG&E" "SDG&E"   {

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition `community_var_list', vce(robust)
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo community_`_label'
    estadd loc Utility "`latex_label'"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_community, replace 
    drop phat ihat error lb ub plb pub 

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition `population_var_list', vce(robust)
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo population_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_population, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo primary_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_primary, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo all_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"
    estadd loc Derived "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_all, replace 
    drop phat ihat error lb ub plb pub 

    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'.tex, se keep(socio sens) pr2 scalars(Utility Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'.csv, replace wide plain se keep(socio sens) pr2 scalars(Utility Population Primary Derived)
    
    restore, preserve
    
}

esttab community* population* all* using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall.tex, se keep(socio sens) pr2 scalars(Utility Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar
esttab community* population* primary* all* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall.csv", replace wide plain se keep(socio sens) pr2 scalars(Utility Population Primary Derived)


// First column: all weather variables, in all service areas, from 2014-2021 

restore, not 
use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"
preserve
eststo clear 

foreach utility in "SCE" "PG&E" "SDG&E"   {

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition `community_var_list', vce(robust)
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo community_`_label'
    estadd loc Utility "`latex_label'"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_community_full_sample, replace 
    drop phat ihat error lb ub plb pub 

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition `population_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo population_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_population_full_sample, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo primary_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_primary_full_sample, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo all_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"
    estadd loc Derived "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_all_full_sample, replace 
    drop phat ihat error lb ub plb pub 

    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'_full_sample.tex, se keep(socio sens) pr2 scalars(Utility Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'_full_sample.csv, replace wide plain se keep(socio sens) pr2 scalars(Utility Population Primary Derived)
    
    restore, preserve
    
}

esttab community* population* all* using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall_full_sample.tex, se keep(socio sens) pr2 scalars(Utility Population  Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar
esttab community* population* all* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall_full_sample.csv", replace wide plain se keep(socio sens) pr2 scalars(Population Utility Primary Derived)

restore, not 
use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
gen log_Pop = log(TotPop19)
label var Utility "Utility"
label var socio "SES Index"
label var sens "Health Index"
gen ignition_or_psps = ignition==1 | psps==1
label var ignition_or_psps "ignition"
preserve
eststo clear 


foreach utility in "SCE" "PG&E" "SDG&E"   {

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition_or_psps `community_var_list', vce(robust)
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo community_`_label'
    estadd loc Utility "`latex_label'"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_community, replace 
    drop phat ihat error lb ub plb pub 

    keep if Utility == "`utility'"
    local _label: subinstr local utility  "&" ""
    local latex_label: subinstr local utility  "&" "\&"

    logit ignition_or_psps `population_var_list', vce(robust)
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo population_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_population_psps_1, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition_or_psps `primary_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo primary_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_primary_psps_1, replace 
    drop phat ihat error lb ub plb pub 

    logit ignition_or_psps `all_var_list', vce(robust) ltolerance(1e-5) nonrtolerance
    predict phat
    predict ihat, xb
    predict error, stdp
    generate lb = ihat - invnormal(0.975)*error
    generate ub = ihat + invnormal(0.975)*error
    generate plb = invlogit(lb)
    generate pub = invlogit(ub)
    eststo all_`_label'
    estadd loc Utility "`latex_label'"
    estadd loc Population "X"
    estadd loc Primary "X"
    estadd loc Derived "X"

    save /nobackup1/vilgalys/data/ignition_prob/`utility'_linear_all_psps_1, replace 
    drop phat ihat error lb ub plb pub 

    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'_psps_1.tex, se keep(socio sens) pr2 scalars(Utility Population Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar 
    esttab *`_label' using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_`utility'_psps_1.csv, replace wide plain se keep(socio sens) pr2 scalars(Utility Population Primary Derived)
    
    restore, preserve
    
}

esttab community* population* all* using /pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall_psps_1.tex, se keep(socio sens) pr2 scalars(Utility Population  Primary Derived) label collabels(none) unstack nomtitles replace nomtitles nodepvar
esttab community* population* all* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/logistic_regression_ignition_overall_psps_1.csv", replace wide plain se keep(socio sens) pr2 scalars(Population Utility Primary Derived)


