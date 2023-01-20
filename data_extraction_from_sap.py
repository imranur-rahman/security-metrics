import csv
import json

# Assuming we have the repository of SAP downloaded in the same directory as this file

# Loading the attackvector and safeguard json file
with open("risk-explorer-for-software-supply-chains/src/data/attackvectors.json", "r", encoding="utf-8") as f:
    attackvectors_json = json.load(f)
# print (attackvectors_json)
with open("risk-explorer-for-software-supply-chains/src/data/safeguards.json", "r", encoding="utf-8") as f:
    safeguards_json = json.load(f)
# print(safeguards_json)

# Open CSV file to store the attackvector data
attackvector_csv = open("attackvectors.csv", "w")
attackvector_header = ["AV ID", "Attack Vector", "Safeguard", "SG ID"]
attackvector_writer = csv.DictWriter(attackvector_csv, fieldnames=attackvector_header)
attackvector_writer.writeheader()

for attackvector in attackvectors_json:
    # print("avId: " + attackvector["avId"])
    extracted_safeguards = []
    infos = attackvector["info"] # This is a list
    for info in infos:
        mapped_safeguards = info["Mapped Safeguard"] # This is a list
        for mapped_safeguard in mapped_safeguards:
            # print("avId: " + attackvector["avId"] + " sgId: " + mapped_safeguard["sgId"])
            # extracted_safeguards.append(mapped_safeguard["sgId"])
            # At this point we have the set of safeguard ids for each attackvector id
    
            # Find the safeguard name (from safeguards.json) for this attackvector
            for safeguard in safeguards_json:
                if safeguard["sgId"] == mapped_safeguard["sgId"]:
                    # Save the name for the safeguard
                    extracted_safeguards.append(safeguard["sgId"] + " " + safeguard["sgName"])

                    # Write this instance of attackvector and safeguard in csv
                    attackvector_writer.writerow({"AV ID": attackvector["avId"],
                                                "Attack Vector": attackvector["avName"],
                                                "Safeguard": safeguard["sgName"],
                                                "SG ID": safeguard["sgId"]})
    print("attackvector: "+ attackvector["avId"] + " " + attackvector["avName"] + "\nsafeguards: ")
    [print (x) for x in extracted_safeguards]
    print("\n")

attackvector_csv.close()

# Open CSV file to store safeguard data
safeguard_csv = open("safeguards.csv", "w")
safeguard_header = ["SG ID", "Safeguard Name", "Description", "Directive", "Preventive", "Detective",
                "Corrective", "Project Maintainer", "Administrator", "Downstream User"]
safeguard_write = csv.DictWriter(safeguard_csv, fieldnames=safeguard_header)
safeguard_write.writeheader()

for safeguard in safeguards_json:
    safeguard_write.writerow({"SG ID": safeguard["sgId"],
                            "Safeguard Name": safeguard["sgName"],
                            "Description": safeguard["info"][0]["Description"],
                            "Directive": safeguard["info"][0]["Directive"],
                            "Preventive": safeguard["info"][0]["Preventive"],
                            "Detective": safeguard["info"][0]["Detective"],
                            "Corrective": safeguard["info"][0]["Corrective"],
                            "Project Maintainer": safeguard["info"][0]["Project Maintainer"],
                            "Administrator": safeguard["info"][0]["Administrator"],
                            "Downstream User": safeguard["info"][0]["Downstream User"],
                            })

safeguard_csv.close()