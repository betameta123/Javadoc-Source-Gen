from bs4 import BeautifulSoup
import requests

def class_sig(soup):
    return soup.find(class_="type-signature").text.replace("\n", " ").replace(chr(13),"") + " {" # class signature

def get_fields(soup):
    job_elements = soup.find(id="field-detail")
    job_elements = job_elements.find_all(class_="member-signature")
    variables = []
    for var in job_elements:
        variables.append(var.text + ";") # add field variables

    return "\t" + "\n\t".join(variables) + "\n"

def method_sig(soup, sec):
    signatures = []
    job_elements = soup.find(id=sec) # section including all the methods
    job_elements = job_elements.find_all(class_="member-signature")

    for signature in job_elements:
        signatures.append("\t{a} {{\n\n\t}}".format(a=signature.get_text())) # method signatures

    return signatures

def java_docs(soup, sec):
    job_elements = soup.find(id=sec)
    job_elements = job_elements.find_all(class_="block") # contains the description
    doc = []

    for block in job_elements:
        doc.append("\t/**\n \t * {a}\n\t *".format(a=block.text.replace("\n","\n\t *").replace(chr(13),""))) # get description

    return doc

def get_tags(soup, sec):
    job_elements = soup.find(id=sec)
    job_elements = job_elements.find_all(class_="notes") # contains the tags
    tags = []

    for job in job_elements:
        s = ""
        token = job.get_text().strip().split("\n")
        for i, t in enumerate(token):
            if i == 0:
                continue
            if token[i-1] == "Parameters:": # Header for a parameter section in compiled javadocs
                s += "\n\t * @param {}".format(token[i].replace(" - "," ")) # get parameters get rid of dash
            elif token[i-1] == "Returns:":
                s+= "\n\t * @return {}".format(token[i].replace(" - "," ")) # get return description
        s+="\n\t */\n" # close the javadocs comment
        tags.append(s)

    return tags

def print_to_file(soup, text):
    file = soup.title.text + ".java"
    with open(file, "a") as f:
        f.write(text)

def main():
    URL = input("Link to JavaDocs: ").strip()
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    full_doc = []

    # Class Stuff
    full_doc.append(class_sig(soup))
    full_doc.append(get_fields(soup))

    # Constructor Stuff
    tags = get_tags(soup, "constructor-detail")
    sig = method_sig(soup,"constructor-detail")
    doc = java_docs(soup, "constructor-detail")
    for parts in zip(doc,tags,sig):
        full_doc.append("".join(parts) + "\n")

    # Method Stuff
    tags = get_tags(soup, "method-detail")
    sig = method_sig(soup,"method-detail")
    doc = java_docs(soup, "method-detail")
    for parts in zip(doc,tags,sig):
        full_doc.append("".join(parts) + "\n")

    full_doc.append("}")
    full_doc = "\n".join(full_doc)

    print("\n--------------------------------------------------------------------\n")
    print("(1) output to file\n(2) output to terminal")

    try:
        mode = int(input("> ").strip())
        if mode == 1:
            print_to_file(soup, full_doc)
        elif mode == 2:
            print(full_doc)
        else:
            print("Your Bad")
    except:
        print("Your bad")
        exit(-1)

if __name__ == '__main__':
  main()
