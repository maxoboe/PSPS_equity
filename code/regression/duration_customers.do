use "/nobackup1/vilgalys/data/gridmet/ignition_and_gridmet_for_stata.dta", clear 
eststo clear 

keep if psps
gen log_customers = log(TOTAL_CUST)
gen log_duration = log(Outage_Hou)
gen log_CMI = log(CMI)
gen log_Pop = log(TotPop19)

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

esttab customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/customers_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nodepvar
esttab customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/customers_regression.csv", replace wide plain se  keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) 


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

esttab CMI* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/CMI_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nodepvar
esttab CMI* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/CMI_regression.csv", replace wide plain se  keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) 

esttab CMI* customers* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/CMI_customers_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) label collabels(none) replace

reg log_duration `community_var_list', robust
eststo duration_community_

reg log_duration `population_var_list', robust
eststo duration_population_
estadd loc Population "X"


// Using primary weather vars 
reg log_duration `primary_var_list', robust

eststo duration_primary_
estadd loc Population "X"
estadd loc Primary "X"

reg log_duration `all_var_list', robust

eststo duration_all_
estadd loc Population "X"
estadd loc Primary "X"
estadd loc Derived "X"

esttab duration* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/duration_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) label collabels(none) unstack nomtitles replace nodepvar
esttab duration* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/duration_regression.csv", replace wide plain se  keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) 


esttab customers* duration* using "/pool001/vilgalys/inferring_expectations/outputs/regressions/customers_duration_regression.tex", se keep(SCE_sens SCE_socio PGE_sens PGE_socio SDGE_sens SDGE_socio) r2 scalars(Population Primary Derived) label collabels(none) replace
