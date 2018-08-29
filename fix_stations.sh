#!/bin/bash

f=staStations.yaml
#grep stationName: staStations.yaml|awk '{ print length, $0 }'|sort -n|cut -d" " -f2-

sed -i 's/ - /-/g' $f
sed -i 's/Moon /M/' $f
sed -i 's/Federation/Fed/' $f 
sed -i 's/Observatory/Observ/' $f 
sed -i 's/Logistic/Logi/' $f 
sed -i 's/Support/Supprt/' $f 
sed -i 's/Imperial/Imp/' $f 
sed -i 's/Laboratory/Lab/' $f 
sed -i 's/Corporation/Corp/' $f 
sed -i 's/Assembly/Assy/' $f
sed -i 's/Facilities/Facils/' $f
sed -i 's/Facility/Facily/' $f
sed -i 's/Reprocessing/Reproc/' $f
sed -i 's/Republic/Repub/' $f
sed -i 's/Services/Serv/' $f
sed -i 's/Advanced/Adv/' $f
sed -i 's/University/Uni/' $f
sed -i 's/ and /&/' $f
sed -i 's/Institute/Inst/' $f
sed -i 's/Chemical/Chem/' $f
sed -i 's/Refinery/Refine/' $f
sed -i 's/Tribunal/Tribe/' $f
sed -i 's/Laboratories/Labs/' $f
sed -i 's/Reserve/Resrv/' $f
sed -i 's/Mineral/Min/' $f
sed -i 's/Acquisition/Acq/' $f
sed -i 's/Pharmaceuticals/Pharma/' $f
sed -i 's/Protection/Protect/' $f
sed -i 's/Depository/Deposit/' $f
sed -i 's/Containment/Contain/' $f
sed -i 's/Constructions/Construct/' $f
sed -i 's/Production/Prod/' $f
sed -i 's/Association/Assoc/' $f
sed -i 's/Directorate/Direct/' $f
sed -i 's/Syndicate/Syndi/' $f
sed -i 's/Administration/Admin/' $f
sed -i 's/Information/Info/' $f
sed -i 's/Intelligence/Intel/' $f
sed -i 's/Development/Dev/' $f
sed -i 's/Distribution/Dist/' $f
sed -i 's/Storage/Stor/' $f
sed -i 's/Biotech Research Center/Biotech/' $f
sed -i 's/Law School/Law/' $f
sed -i 's/Bureau Offices/Bureau/' $f
#sed -i 's///' $f

