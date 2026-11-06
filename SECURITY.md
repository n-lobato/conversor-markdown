# Segurança e relato de vazamentos

O Conversor Markdown lida com documentos que contêm dados pessoais. Por isso, alguns problemas não devem ser relatados em issues públicas.

## O que relatar em particular

Relate em particular qualquer situação em que um dado pessoal **continua acessível** num arquivo que o programa entregou como limpo. Por exemplo:

- um arquivo `_anonimizado.md` que ainda contém um dado que a tela de revisão mostrou como trocado;
- qualquer arquivo gravado depois de a revisão ter sido cancelada ou de a anonimização ter falhado;
- qualquer envio de dados para fora do computador, que o programa promete não fazer.

Um nome que **não foi detectado** e aparece normalmente no texto é limitação conhecida da detecção automática (veja a seção sobre anonimização no README). Pode ser relatado como issue pública, desde que com exemplo inventado.

## Como relatar

Use o botão **Report a vulnerability**, na aba **Security** deste repositório, ou o link [relatar em particular](https://github.com/n-lobato/conversor-markdown/security/advisories/new). O relato fica visível só para o autor.

**Nunca envie o documento real**, nem mesmo em particular. Descreva o problema e, se possível, monte um arquivo de teste com dados inventados que reproduza a falha.

## Versões corrigidas

As correções saem na versão mais recente, publicada em [Releases](https://github.com/n-lobato/conversor-markdown/releases). Versões anteriores não recebem correção.

## Prazo

Este é um projeto mantido por uma pessoa, sem garantia de prazo. O relato será lido e respondido assim que possível. Problemas que exponham dados pessoais têm prioridade sobre qualquer outro trabalho no projeto.
