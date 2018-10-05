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
sed -i 's/XIV-M/14-M/' $f # ordering is important here
sed -i 's/XVIII-M/18-M/' $f
sed -i 's/XVII-M/17-M/' $f
sed -i 's/XVI-M/16-M/' $f
sed -i 's/XV-M/15-M/' $f
sed -i 's/VIII-M/8-M/' $f
sed -i 's/VII-M/7-M/' $f
sed -i 's/VI-M/6-M/' $f
sed -i 's/XIX-M/19-M/' $f
sed -i 's/IX-M/9-M/' $f
sed -i 's/IV-M/4-M/' $f
sed -i 's/XIII-M/13-M/' $f
sed -i 's/XII-M/12-M/' $f
sed -i 's/XI-M/11-M/' $f
sed -i 's/III-M/3-M/' $f
sed -i 's/II-M/2-M/' $f
sed -i 's/I-M/1-M/' $f
sed -i 's/X-M/10-M/' $f
sed -i 's/V-M/5-M/' $f
sed -i 's/M40-/M40 /' $f
sed -i 's/M39-/M39 /' $f
sed -i 's/M38-/M38 /' $f
sed -i 's/M37-/M37 /' $f
sed -i 's/M36-/M36 /' $f
sed -i 's/M35-/M35 /' $f
sed -i 's/M34-/M34 /' $f
sed -i 's/M33-/M33 /' $f
sed -i 's/M32-/M32 /' $f
sed -i 's/M31-/M31 /' $f
sed -i 's/M30-/M30 /' $f
sed -i 's/M29-/M29 /' $f
sed -i 's/M28-/M28 /' $f
sed -i 's/M27-/M27 /' $f
sed -i 's/M26-/M26 /' $f
sed -i 's/M25-/M25 /' $f
sed -i 's/M24-/M24 /' $f
sed -i 's/M23-/M23 /' $f
sed -i 's/M22-/M22 /' $f
sed -i 's/M21-/M21 /' $f
sed -i 's/M20-/M20 /' $f
sed -i 's/M19-/M19 /' $f
sed -i 's/M18-/M18 /' $f
sed -i 's/M17-/M17 /' $f
sed -i 's/M16-/M16 /' $f
sed -i 's/M15-/M15 /' $f
sed -i 's/M14-/M14 /' $f
sed -i 's/M13-/M13 /' $f
sed -i 's/M12-/M12 /' $f
sed -i 's/M11-/M11 /' $f
sed -i 's/M10-/M10 /' $f
sed -i 's/M9-/M9 /' $f
sed -i 's/M8-/M8 /' $f
sed -i 's/M7-/M7 /' $f
sed -i 's/M6-/M6 /' $f
sed -i 's/M5-/M5 /' $f
sed -i 's/M4-/M4 /' $f
sed -i 's/M3-/M3 /' $f
sed -i 's/M2-/M2 /' $f
sed -i 's/M1-/M1 /' $f
#sed -i 's///' $f

