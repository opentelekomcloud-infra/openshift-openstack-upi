#!/usr/bin/env bash

for item in $(oc get csr | grep "Pending" | cut -d " " -f 1); do  
  oc adm certificate approve $item
done
