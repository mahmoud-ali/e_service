# Permissions Matrix

User get permissions according to group and application instance state.

## Groups

| # | group | description |
|---|---|---|
| 1 | eom_pub | Executive Office Manager |
| 2 | dga_pub | Director of the General Administration Manager |
| 3 | sd_pub | Supply Department Manager |
| 4 | doa_pub | Director of Administrative Manager |
| 5 | it_pub | Information technology Manager |
| 6 | dgdhra_pub | Director of the General Department of Human Resources and Administration Manager |
| 7 | dgfa_pub | Director of the General Department of Financial Affairs Manager |
| 8 | agmfa_pub | Assistant General Manager for Financial and Administrative Affairs Manager |
| 9 | gm_pub | General Manager |

## Create Operation
* `eom_pub` group are responsible for creating new application.

## Matrix of permissions based on groups and approval status

| # | approval status | Read operation | Update operation | Delete operation |
|---|---|---|---|---|
| 1 | draft | eom_pub | eom_pub,dga_pub | eom_pub |
| 2 | dga_approval | eom_pub,dga_pub,sd_pub | sd_pub | - |
| 3 | dga_rejection | eom_pub,dga_pub | - | - |
| 4 | sd_comment | eom_pub,dga_pub,sd_pub,doa_pub | - | - |
| 5 | doa_comment | eom_pub,dga_pub,sd_pub,doa_pub,it_pub | - | - |
| 6 | it_comment | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub | - | - |
| 7 | dgdhra_recommendation | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub | - | - |
| 8 | dgfa_recommendation | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub,agmfa_pub | - | - |
| 9 | agmfa_approval | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub,agmfa_pub,gm_pub | - | - |
| 10 | agmfa_rejaction | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub,agmfa_pub | - | - |
| 11 | gm_approval | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub,agmfa_pub,gm_pub | - | - |
| 12 | gm_rejaction | eom_pub,dga_pub,sd_pub,doa_pub,dgdhra_pub,dgfa_pub,agmfa_pub,gm_pub | - | - |