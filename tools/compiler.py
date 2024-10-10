#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import re
import difflib

def askOllama(prompt):
    import requests

    base_url = 'http://localhost:11434'
    endpoint = '/api/generate'

    prompt = prompt.strip()

    payload = {
        "model": "llama3.1:latest", 
        "stream": False,                            
        "prompt": prompt
    }
    response = requests.post(base_url + endpoint, json=payload)
    if response.status_code == 200:
        answer = response.json().get("response")
        if answer[0] == '"':
            answer = answer[1:]
        if answer[-1] == '"':
            answer = answer[0:-1]
        return str(answer)
    else:
        print("ollama error")
        exit(1)
        return None

def separate_latin_and_non_latin(text):
    latin_pattern = re.compile(r'[A-Za-z]+')
    non_latin_pattern = re.compile(r'[^\x00-\x7F]+')

    result = []
    i = 0

    while i < len(text):
        if text[i].isascii() and text[i].isalpha():
            match = latin_pattern.match(text, i)
            if match:
                result.append(match.group())
                i = match.end()
        elif not text[i].isascii():
            match = non_latin_pattern.match(text, i)
            if match:
                result.append(match.group())
                i = match.end()
        else:
            result.append(text[i])
            i += 1

    return ' '.join(result).strip()

def replace_similar_latin_words(text1, text2):
    text1_words = text1.split()
    text2_words = text2.split()
    latin_pattern = re.compile(r'^[a-zA-Z]+$')
    text1_latin_words = [word for word in text1_words if latin_pattern.match(word)]
    result = []
    for word2 in text2_words:
        if latin_pattern.match(word2):
            matches = difflib.get_close_matches(word2.lower(), text1_latin_words, n=1, cutoff=0.3)
            if matches:
                result.append(matches[0])
            else:
                result.append(word2)
        else:
            result.append(word2)
    return ' '.join(result)

parser = argparse.ArgumentParser(description="Wordpress post compiler.")
parser.add_argument("--input", required=True, help="Input file path.")
parser.add_argument("--output", required=True, help="Output file path.")

args = parser.parse_args()
inputFile = args.input
outputFile = args.output

inputFileLines = open(inputFile, "r").readlines()

if len(inputFileLines) < 5:
    print("\
          Post must contains at least 5 lines.\n\
          Format: format code\n\
          Language: post language code\n\
          Title: post title\n\
          Slug: post_slug\n\
          Categories: categories separated by comma\n\
          Post content\
          ")
    exit(1)

supportingFormatCode = "Fall24-October10"

formatCode = inputFileLines[0].strip()[len("Format: "):]

if formatCode != supportingFormatCode:
    print(f"Can't process file with formatCode: \"{formatCode}\", because compiler supports \"{supportingFormatCode}\" only")
    exit(1)

language = inputFileLines[1].strip()[len("Language: "):]
title = inputFileLines[2].strip()
slug = inputFileLines[3].strip()
categories = inputFileLines[4].strip()[len("Categories: "):].split(",")
inputFileLines = inputFileLines[5:]

print(f"Post_title: {title}")
print(f"Slug: {slug}")

if title.startswith("Title: ") == False:
    print("Title line must start with \"Title:\" prefix")
    exit(1)

if slug.startswith("Slug: ") == False:
    print("Slug line must start with \"Slug:\" prefix")
    exit(1)

title = title[len("Title: "):]
slug = slug[len("Slug: "):]

outputFileDescriptor = open(outputFile, "w")

state = "text"
codeStateLanguage = "Bash"
previousState = "text"
textBlock = ""
outputText = ""

def translate(text, type, source, destination):
    print(f"translate {source} -> {destination} by {type}")

    if type == "google":
        from googletrans import Translator
        translator = Translator()
        for i in range(0, 10):
            try:
                outputText = translator.translate(text, src=source, dest=destination).text
                break
            except Exception as error:
                print(error)
                
        return outputText

    elif type == "openai":
        from openai import OpenAI

        client = OpenAI(
            api_key=open("./private/openAI_api_key", "r").read().strip()
        )        
        chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say this is a test",
            }
        ],
        model="gpt-3.5-turbo",
        )
        return chat_completion['choices'][0]['message']['content'].strip()
    
    elif type == "ollama":
        prompt = f"""
            Translate text: \"{text}\" from \"{source}" to \"{destination}". Context is programmer blog. I need only translation, without additional comments from your side, also no additional quotes, so I can copy and paste your output directly into file.       
            """    
        answer = askOllama(prompt)    
        print(answer)
        return answer

codeEscapedSymbols = [
    ("<","&lt;"),
    (">","&gt;"),
    ('"',"&quot;"),
]

def processLine(line, state):
    outputLine = line

    if state == "code":
        for codeEscapedSymbol in codeEscapedSymbols:
            outputLine = outputLine.replace(codeEscapedSymbol[0], codeEscapedSymbol[1])

    return outputLine

def processLink(line):
    outputLine = line.replace("http://", "https://")
    outputLine = outputLine.strip()
    outputLine = f"<a href=\"{outputLine}\" rel=\"noopener\" target=\"_blank\">{outputLine}</a>\n"

    return outputLine

lastLineIndex = len(inputFileLines) - 1

languageCodes = ["ru", "en", "zh", "de"]
googleTranslateLanguageCodes = ["ru", "en", "zh-cn", "de"]
originalLanguageCode = "ru"

def translateTitle(title):
    if title.startswith("[DO NOT PROCESS LINE]"):
        return title[len("[DO NOT PROCESS LINE]"):]
    
    output = f"{{:{originalLanguageCode}}}{title}{{:}}"
    for i in range(len(languageCodes)):
        if languageCodes[i] == originalLanguageCode:
            continue
        output += f"{{:{languageCodes[i]}}}"
        #output += replace_similar_latin_words(title, separate_latin_and_non_latin(translate(title, "ollama", originalLanguageCode, googleTranslateLanguageCodes[i])))
        output += translate(title, "ollama", originalLanguageCode, googleTranslateLanguageCodes[i])
        output += "{:}"
    return output

outputFileDescriptor.write(slug)
outputFileDescriptor.write("\n")
outputFileDescriptor.write(translateTitle(title))
outputFileDescriptor.write("\n")
outputFileDescriptor.write(",".join(categories))
outputFileDescriptor.write("\n")

for i in range(len(languageCodes)):
    targetLanguageCode = languageCodes[i]
    outputFileDescriptor.write(f"{{:{targetLanguageCode}}}")
    for lineIndex, line in enumerate(inputFileLines):
        print(f"line: {line}")
        if line.startswith("[DO NOT PROCESS LINE]"):
            outputFileDescriptor.write(line[len("[DO NOT PROCESS LINE]"):])  
            continue        
        elif line.startswith("<pre><code>"):
            state = "code-start"
            if len(line.split("<pre><code>Language: ")) != 2:
                print("Code line header must contains Language name!")
                exit(1)                   
            codeStateLanguage = line.split("<pre><code>Language: ")[1].strip()
        elif state == "code-start":
            state = "code"
        elif line.startswith("</code></pre>"):
            state = "code-end"
        elif state == "code-end":
            state = "text"
        elif state == "link":
            state = "text"
        elif len(line) < 2:
            print("len(line) < 2")
            state = "text-end"
        elif state == "text-end" and len(line) > 1:
            state = "text"
            outputFileDescriptor.write("\n")
        
        if line.startswith("http://") or line.startswith("https://"):
            state = "link"

        if previousState == "text" and state != "text":
            if targetLanguageCode != originalLanguageCode:
                outputText = translate(textBlock, "google", originalLanguageCode, googleTranslateLanguageCodes[i]).rstrip('\n') + '\n'
            else:
                outputText = textBlock

            print(outputText)
            outputFileDescriptor.write(outputText)
            textBlock = ""

        codeBlockHeader = f"<div class=\"hcb_wrap\"><pre class=\"prism undefined-numbers lang-{codeStateLanguage.lower()}\" data-lang=\"{codeStateLanguage}\"><code>"
        codeBlockFooter = "</code></pre></div>"

        if previousState == "code" and state == "code-end":
            outputFileDescriptor.write(f"{codeBlockHeader}{textBlock.lstrip()}{codeBlockFooter}\n")
            textBlock = ""

        if state == "link":
            outputFileDescriptor.write(processLink(line))
            textBlock = ""

        if state != "code-start" and state !="code-end" and state != "link":
            textBlock += processLine(line, state)

        previousState = state
    outputFileDescriptor.write("{:}")