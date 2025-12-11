# JSON.MD

## Le JSON de basae

LE JSON DOIT ABSOLUMENT CONVENIR A CE FORMAT, AINSI QU'AUX ENUMS

```json
{
  "type": "type_enum",
  "value": "..."
}
```

> Le type_enum, est une valeur contenu dans l'enumeration juste en bas

## Les types et leurs valeurs

### Pinguin qui parle

```json
{
  "type": "pinguin_message",
  "value": "AudioBase64" -> Tableau FLOAT
}
```
> Ici le pinguin qui va écouter le son dans l'étape 1, il va envoyer un tableau de tout le
> son enregistré uniquement à partir du moment où la VAD s'est activé et lorsqu'elle
> ne detecte plus de bruits

### Le nom est écrit sur le scrabble

```json
{
  "type": "name_is_writen",
  "value": true
}
```