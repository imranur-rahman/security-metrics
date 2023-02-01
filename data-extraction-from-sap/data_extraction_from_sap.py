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
with open("risk-explorer-for-software-supply-chains/src/data/references.json", "r", encoding="utf-8") as f:
    references_json = json.load(f)
with open("risk-explorer-for-software-supply-chains/src/data/taxonomy.json", "r", encoding="utf-8") as f:
    taxonomy_json = json.load(f)

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

        # If the list is empty, add an empty safeguard to keep the attack
        # vector in the CSV file
        if len(mapped_safeguards) > 0:
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
                        attackvector_writer.writerow({
                            "AV ID": attackvector["avId"],
                            "Attack Vector": attackvector["avName"],
                            "Safeguard": safeguard["sgName"],
                            "SG ID": safeguard["sgId"]
                        })
        else:
            attackvector_writer.writerow({
                "AV ID": attackvector["avId"],
                "Attack Vector": attackvector["avName"],
                "Safeguard": "",
                "SG ID": ""
            })
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
    safeguard_write.writerow({
        "SG ID": safeguard["sgId"],
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

# Open CSV file to store reference data
reference_csv = open("references.csv", "w")
reference_header = ["title", "link", "avId", "avName", "sgId", "sgName",
                    "ecosystems", "packages", "contents", "year"]
reference_write = csv.DictWriter(reference_csv, fieldnames=reference_header)
reference_write.writeheader()

for reference in references_json:
    # There could be multiple vectors and multiple safeguards
    # So for now writing all possible combinations

    # Saving the values for each key in a list
    # and if that key doesn't exist in a certain object, fillup with empty string
    # This is important since later we are doing multiple nested loops

    # Gather the attack vectors first
    vectors = []
    if reference.get("vectors") is not None:
        vectors = [ vector for vector in reference["vectors"] ]
    else:
        vectors = [{
            "avId": "",
            "avName": ""
        }]

    # Gather the safeguards next
    safeguards = []
    if reference.get("safeguards") is not None:
        safeguards = [safeguard for safeguard in reference["safeguards"]]
    else:
        safeguards = [{
            "sgId": "",
            "sgName": ""
        }]

    # Gather the ecosystems
    ecosystems = []
    if reference["tags"].get("ecosystems") is not None and len(reference["tags"]["ecosystems"]) > 0:
        ecosystems = [ecosystem for ecosystem in reference["tags"]["ecosystems"]]
    else:
        ecosystems = [""]

    packages = []
    if reference["tags"].get("packages") is not None and len(reference["tags"]["packages"]) > 0:
        packages = [package for package in reference["tags"]["packages"]]
    else:
        packages = [""]

    contents = []
    if reference["tags"].get("contents") is not None and len(reference["tags"]["contents"]) > 0:
        contents = [content for content in reference["tags"]["contents"]]
    else:
        contents = [""]

    if reference["tags"].get("year") is not None:
        year = reference["tags"]["year"]
    else:
        year = ""
    
    for vector in vectors:
        for safeguard in safeguards:
            for ecosystem in ecosystems:
                for package in packages:
                    for content in contents:
                        reference_write.writerow({
                            "title": reference["title"],
                            "link": reference["link"],
                            "avId": vector["avId"],
                            "avName": vector["avName"],
                            "sgId": safeguard["sgId"],
                            "sgName": safeguard["sgName"],
                            "ecosystems": ecosystem,
                            "packages": package,
                            "contents": content,
                            "year": year
                        })

reference_csv.close()

# A recursive helper function to write rows for each attackvector and it's children (attack vectors)
# If the child has more children (more child attack vector) recursively call this func for that child

# Taxonomy (of attack vectors) is a tree and we are running this recursive func for
# each node (attack vector) of the tree
def taxonomy_writerow(taxonomy_write, attackvector, children):
    for child in children:
        taxonomy_write.writerow({
            "avName": attackvector["avName"],
            "avId": attackvector["avId"],
            "childAvName": child["avName"],
            "childAvId": child["avId"]
        })
        if child.get("children") is not None:
            taxonomy_writerow(taxonomy_write, child, child["children"])

# Open CSV to store taxonomy of attack vectors
taxonomy_csv = open("taxonomy.csv", "w")
taxonomy_header = ["avName", "avId", "childAvName", "childAvId"]
taxonomy_write = csv.DictWriter(taxonomy_csv, fieldnames=taxonomy_header)
taxonomy_write.writeheader()

# Recursively write <attack vector, child attack vector>
taxonomy_writerow(taxonomy_write=taxonomy_write, attackvector=taxonomy_json, 
                    children=taxonomy_json["children"])

taxonomy_csv.close()