# Registro de validação — CODE QUEST

Validação inicial em **22 de outubro de 2026**.

- **19 testes automatizados aprovados**, com Python 3.12 e biblioteca padrão.
- SVG XML válido, referências internas válidas, sem scripts, imagens externas,
  `foreignObject` ou fontes remotas; geração determinística e orçamento de
  tamanho de 250 kB verificados.
- Primeira fonte real: calendário público oficial do GitHub, 369 dias em
  53 semanas. O total e a origem atuais estão em `assets/code-quest/calendar.json`.
- Inspeção visual em navegador Chromium: entrada, corrida, primeiro salto,
  coleta, chegada à bandeira, conclusão e reinício. Corrigidos o espaçamento
  dos primeiros rótulos mensais e o recorte da entrada pelo portal.
- Composição inspecionada também com largura de 360 px, sem corte do gráfico.
  Os rótulos secundários ficam pequenos nessa escala; a imagem tem link para
  abertura em tamanho integral.
- Apresentação estática inspecionada em uma página local que aplica as mesmas
  regras de movimento reduzido. A preferência nativa do sistema operacional
  não foi alternada durante esse teste.
- O SVG também foi aberto como um `<img>` externo em um README local de
  revisão, confirmando carregamento em 1200×520, escala responsiva e animação
  nesse contexto. Isso não substitui o teste no domínio do GitHub.
- YAML do workflow analisado com parser e conferência de gatilhos/permissões.
  Os SHAs das ações foram comparados às tags oficiais no GitHub.
- `preview.png` registra a cena de conclusão da geração inicial. Ele não é
  atualizado pelo workflow e não deve ser usado para consultar o total atual.

## Publicação e execução remota

A implementação está pronta para `PedroCostinha/PedroCostinha`, branch remota
`main`. A publicação foi impedida por autenticação/permissão no ambiente:

- O conector GitHub conseguiu ler o repositório, mas recusou a criação de blob
  com **HTTP 403 — `Resource not accessible by integration`**.
- O Git Credential Manager local não forneceu credencial não interativa.
- O teste de push sem interação falhou por ausência de usuário/credencial.
- O navegador disponível abriu o repositório sem sessão autenticada.

Nenhuma configuração administrativa, credencial ou proteção foi alterada.
O README remoto permanece sem esta animação. O workflow ainda **não foi
executado**, e a exibição dentro do README do GitHub **não foi validada**.
Essa validação é uma pendência real, não uma compatibilidade presumida.

Para publicar o commit local, autentique o Git com uma conta que tenha escrita
nesse repositório e permissão para adicionar workflows, ou reconecte a
integração com as permissões correspondentes. Com o commit revisado:

```sh
git push origin feat/code-quest:main
```

O envio é normal, sem force. Se `main` avançou ou estiver protegida, não force:
atualize o trabalho e use o fluxo de PR exigido pelo repositório. O push do
código inicia automaticamente o workflow; acompanhe em
[Actions](https://github.com/PedroCostinha/PedroCostinha/actions/workflows/update-code-quest.yml).
Após a execução, confira `source: github-graphql` nos dados e a imagem animada
no README renderizado. Firefox/Edge e dispositivos físicos continuam sujeitos
à cobertura descrita abaixo.

## Limitações de cobertura

Não houve execução independente em Firefox, Edge, Safari/iOS ou dispositivo
Android físico. O teste de largura móvel utiliza o navegador Chromium do
ambiente de revisão. O suporte nesses produtos não foi certificado apenas por
inferência. O SVG usa animações CSS e referências internas SVG padrão; não
depende de execução de JavaScript pelo GitHub.
