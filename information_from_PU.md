# Getting information from PU
PU work in a Google Docs document using a single table in the document. We can get it as an ODT file and parse the content.xml file to get the information. The content.xml file contains the table with the information we need.

The URL downloaded from when we click on "Download as ODT" can easily be obtained by clicking on "Download as ODT" and copying the URL from the browser.

Google AI suggested changing `/edit` to `/export?format=odt` to download the ODT file directly. So the link to download the newest ODT file is:

```
https://docs.google.com/document/d/[XYZ]/export?format=odt
```
