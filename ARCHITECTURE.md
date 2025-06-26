Dette dokument beskriver en ide til projektets arkitektur.

Figuren nedenfor beskriver det overordnet.

```d2
Google Kalender

dovenKalender: {
  kalender
  poster: {
    api
    manual
    selenium
  }
  generator: {
    ollama
    chatgpt
    lechat
  }
}

Google Kalender <- dovenKalender.kalender
dovenKalender.kalender -> dovenKalender.generator -> dovenKalender.poster

dovenKalender.poster -> Facebook
```
