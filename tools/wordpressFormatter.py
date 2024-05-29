#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

inputFile = sys.argv[1]
outputFile = sys.argv[2]

englishTranslationNeeded = "--translate-to-english" in sys.argv

inputFileLines = open(inputFile, "r").readlines()
outputFileDescriptor = open(outputFile, "w")

translationEngineType = "google"
state = "text"
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

for lineIndex, line in enumerate(inputFileLines):

    if line.startswith("<pre><code>"):
        state = "code-start"
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


    if previousState == "code" and state == "code-end":
        outputFileDescriptor.write(f"<pre><code>\n{textBlock}</code></pre>\n")
        textBlock = ""

    if state == "link":
        outputFileDescriptor.write(processLink(line))
        textBlock = ""

    if state != "code-start" and state !="code-end" and state != "link":
        textBlock += processLine(line, state)

    previousState = state