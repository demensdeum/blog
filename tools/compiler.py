#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse

parser = argparse.ArgumentParser(description="Wordpress post compiler.")
parser.add_argument("--input", required=True, help="Input file path.")
parser.add_argument("--output", required=True, help="Output file path.")

args = parser.parse_args()
inputFile = args.input
outputFile = args.output

inputFileLines = open(inputFile, "r").readlines()

if len(inputFileLines) < 3:
    print("Post must contains at least 3 lines.\nTitle: Post title\nSlug: post_slug\nPost content")
    exit(1)

title = inputFileLines[0].strip()
slug = inputFileLines[1].strip()

inputFileLines = inputFileLines[2:]

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

translationEngineType = "google"
state = "text"
codeStateLanguage = "Bash"
previousState = "text"
textBlock = ""
outputText = ""

def translate(text, type):
    if type == "google":
        from googletrans import Translator
        translator = Translator()
        return translator.translate(text).text

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

outputFileDescriptor.write(slug)
outputFileDescriptor.write("\n")
outputFileDescriptor.write(title)
outputFileDescriptor.write("\n")

for i in range(2):
    englishTranslationNeeded = i == 0
    if englishTranslationNeeded:
        outputFileDescriptor.write("{:en}")
    else:
        outputFileDescriptor.write("{:ru}")
    for lineIndex, line in enumerate(inputFileLines):
        if line.startswith("<pre><code>"):
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
        
        if line.startswith("http://") or line.startswith("https://"):
            state = "link"

        if previousState == "text" and state != "text":
            if englishTranslationNeeded and len(textBlock) > 0:
                outputText = translate(textBlock, translationEngineType).rstrip('\n') + '\n'
            else:
                outputText = textBlock

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