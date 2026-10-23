# CODE QUEST — Pedro Costinha

A V2 é uma fase original em pixel art sobre o calendário real de contribuições de
**PedroCostinha**. O SVG é autocontido: não usa JavaScript, imagens remotas,
fontes externas, Canvas ou `foreignObject`. O ciclo dura **20,8 segundos**.

## O que o gráfico significa

Cada quadrado é um dia real, com data, quantidade agregada de contribuições e
nível de atividade fornecidos pelo GitHub. As semanas avançam da esquerda para
a direita; domingo ocupa a primeira linha. Dias anteriores ou posteriores ao
intervalo retornado não recebem quadrados inventados.

O grafite representa ausência de contribuições. Quatro tons de vermelho
representam os quatro níveis relativos da API, não intervalos fixos de commits.
A borda superior do calendário forma o percurso. O maior nível de atividade de
cada grupo de seis semanas determina sua elevação (0–16 px); grupos finais com
menos de três semanas são unidos ao anterior. As fundações ficam acima da
primeira linha e não cobrem nenhum dia. Um contorno vermelho temporário percorre
as semanas em sincronia com a posição horizontal do explorador; os preenchimentos
e as contagens originais permanecem intactos.

Cada grupo com atividade de nível 3 ou 4 pode oferecer uma moeda, alinhada à
semana de um dia real desse nível. Selecionamos por nível, contagem e data,
com desempate determinístico. A moeda acompanha a altura exata da trajetória,
inclusive durante saltos; na coleta, o dia de origem recebe um contorno dourado.
**Uma moeda não equivale a um commit.** Um ano com pouca atividade pode ter poucas
moedas ou nenhuma.

`calendar.json` guarda somente login público, origem, total e os agregados de
cada dia. Não consultamos nomes de repositórios, commits, empresas, mensagens ou
autores. A visibilidade dos agregados privados depende do que o GitHub permite
mostrar para a credencial usada; a animação não promete reproduzir o histórico
privado visto pelo titular autenticado.

## Arquitetura

| Arquivo | Responsabilidade |
| --- | --- |
| `scripts/generate_code_quest.py` | CLI, reprodução e escrita somente quando há mudanças |
| `scripts/code_quest/data.py` | GraphQL, tentativas limitadas e validação do calendário |
| `scripts/code_quest/motion.py` | Plataformas, parábolas, poses e instante de coleta |
| `scripts/code_quest/sprites.py` | Explorador original, quadros e alfabeto vetorial 5×7 |
| `scripts/code_quest/scene.py` | Cenário, calendário, cronogramas CSS e validação XML |
| `assets/code-quest/calendar.json` | Dados agregados reais utilizados na geração |
| `assets/code-quest/code-quest.svg` | Arte animada incorporada ao README |
| `assets/code-quest/code-quest-static.svg` | Mesmos dados e cena final, sem animações; fonte alternativa do picture |
| `assets/code-quest/preview.png` | Fotograma de apresentação; não é o calendário atualizado |
| `tests/test_code_quest.py` | Testes lógicos e de integridade |
| `.github/workflows/update-code-quest.yml` | Testes e atualização diária |

O explorador usa uma grade original de 20×24 pixels, com escala 1,75 e altura
máxima de 42 px no SVG (V1: 40 px). Tem seis quadros distintos de corrida e
15 poses: idle, aceleração, corrida, subida, ápice, queda, aterrissagem, coleta,
vitória e comemoração. A mesma trajetória calcula movimento, coleta, partículas,
contador e passagem pelas semanas. O personagem acelera suavemente por 0,32 s;
depois mantém velocidade horizontal constante. Os saltos
começam antes das bordas, respeitam a largura do personagem e terminam sobre
o patamar seguinte. Poeira acompanha as aterrissagens. Nuvens, estrelas,
silhuetas da cidade e bandeira completam o cenário sem alterar os dados.

O calendário permanece estável. A camada cinematográfica desaparece suavemente
no final e reaparece no início, ocultando a reposição do personagem e moedas.
`prefers-reduced-motion: reduce` desliga as animações CSS e mostra o calendário,
personagem parado junto à bandeira, contador final e mensagem de conclusão.
O README também usa `<picture>` com uma fonte SVG estática para essa preferência.
Isso evita depender da propagação de preferências para SVGs dentro de `<img>`;
na emulação local do Chrome, essa propagação não aconteceu, embora o SVG aberto
diretamente respeitasse a preferência. O arquivo estático é gerado do mesmo
calendário, validado e atualizado junto com a versão animada.

## Gerar e testar

Requer Python 3.12 ou posterior, somente com a biblioteca padrão. Na raiz:

```sh
python -m unittest discover -s tests -v
python scripts/generate_code_quest.py --check
```

Para atualizar com dados novos, disponibilize `GITHUB_TOKEN` no ambiente e rode:

```sh
python scripts/generate_code_quest.py
```

O token é lido apenas da variável de ambiente. Não o coloque no código, em
argumentos de linha de comando ou em arquivos do repositório. No Actions,
o workflow fornece o token temporário criado pelo GitHub automaticamente.

Para reproduzir exatamente a arte existente sem consultar a rede:

```sh
python scripts/generate_code_quest.py --calendar assets/code-quest/calendar.json
```

O modo de reprodução é explícito. O modo normal exige token e **nunca recorre
silenciosamente a dados simulados, vazios ou ao cache**. Dados simulados são
criados somente pelos testes. `--check` verifica correspondência integral entre
as células dos dois SVGs e os dados, estrutura XML, IDs/referências, tamanho e
reprodutibilidade. O orçamento máximo do SVG é 250 kB, com viewBox 1200×520.

## Atualização diária

O workflow executa diariamente às **08:17 UTC / 05:17 de Brasília**, aceita
`workflow_dispatch` e também roda quando seu código muda em `main`. Agendamentos
do GitHub podem atrasar; não são um serviço com horário garantido.

O job de testes tem apenas `contents: read`. O job de atualização usa apenas
`contents: write`, necessário para publicar calendário e dois SVGs. A consulta
GraphQL solicita exclusivamente `contributionCalendar` com dias e total.
As ações de checkout e Python estão fixadas por SHA. Na revisão de 23/10/2026,
foram atualizadas para `checkout v7.0.1` e `setup-python v7.1.0`, ambas com runtime
Node 24, mantendo Python 3.12. `ubuntu-24.04` fixa o sistema conhecido durante
a migração de `ubuntu-latest` para 26.04. Gatilhos, token, permissões e horário
foram preservados. O job inclui o SVG estático na publicação condicionada a diff.

Referências oficiais da atualização: [checkout v7.0.1](https://github.com/actions/checkout/releases/tag/v7.0.1),
[setup-python v7.1.0](https://github.com/actions/setup-python/releases/tag/v7.1.0),
[retirada do Node 20](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/)
e [migração do Ubuntu](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/). Pull requests executam
somente testes, sem o job que escreve no repositório.

Erros transitórios de rede, HTTP 429/5xx e limites explícitos recebem até quatro
tentativas com espera limitada. Erros de autenticação, respostas incompletas,
datas inconsistentes e erros GraphQL abortam. A consulta e a geração precisam
terminar e passar na validação antes da substituição dos artefatos. Se qualquer
etapa falhar no Actions, não haverá commit e o último gráfico publicado será
preservado. Conteúdo idêntico não gera um novo commit.

O push é normal, sem force, para a branch padrão informada pelo evento. Se a
branch avançar durante a execução ou uma regra impedir o push, o job falhará
explicitamente. O workflow não contorna proteções e não altera configurações.

Se a organização desabilitar Actions, será necessário habilitar sua execução em
**Settings → Actions → General**. Se uma política impedir `contents: write` ou
exigir PR em `main`, a atualização automática direta não poderá publicar: o
responsável precisa adotar um fluxo de PR compatível com essa política. Não é
necessário criar um token pessoal para o fluxo implementado.

## Origem da primeira geração

O ambiente local de implementação não tinha credencial GraphQL disponível e
o conector GitHub não expunha essa consulta. A primeira geração foi obtida
diretamente de `https://github.com/users/PedroCostinha/contributions`, lendo
datas/níveis das células e quantidades dos tooltips públicos oficiais. Essa
origem é identificada como `github-public-calendar` no JSON e no SVG, sem
fabricar números. Esse carregamento inicial não é um fallback do gerador.

Uma atualização bem-sucedida do workflow substitui a origem por
`github-graphql`. A origem efetiva pode ser conferida em `calendar.json` e em
`<metadata>` no SVG. O intervalo cobre as semanas retornadas pelo GitHub,
incluindo semanas parciais; não é arbitrariamente truncado para 365 células.

## Verificação e compatibilidade

Os testes cobrem anos de 52, 53 e 54 semanas, semanas parciais, zero e alta
atividade, datas duplicadas/ausentes, totais e níveis incoerentes, respostas
inválidas, autenticação, indisponibilidade e limite de requisições. Colisões
são verificadas em milhares de posições com toda a largura de 35 px do sprite;
coletas são conferidas contra a posição e o nível real do patamar.

A revisão visual usa entrada, corrida, primeiro salto, coleta, aproximação da
bandeira, conclusão e transição de reinício. O README usa imagem responsiva
com largura máxima limitada pelo próprio GitHub. Textos principais usam
desenhos vetoriais; os pequenos rótulos de data usam fontes monospace locais.
Em telas pequenas, o calendário anual continua completo e seus rótulos
secundários ficam naturalmente menores; o link da imagem permite ampliar.

O estado da validação efetivamente realizada, incluindo GitHub renderizado e
limitações de navegadores, está em [CODE_QUEST_VALIDATION.md](CODE_QUEST_VALIDATION.md).
Não se deve deduzir compatibilidade com um navegador apenas pela sintaxe SVG.

## Referências estudadas

- [Platane/snk](https://github.com/Platane/snk): exportação de calendário em SVG
  com animações CSS e uso em README.
- [Mario Contribution Graph](https://github.com/sapthesh/Mario-Contribution-Graph):
  consulta GraphQL e composição de um cenário de plataforma. A implementação
  aqui valida o calendário e falha explicitamente em vez de criar uma fase vazia.
- [adrijshikhar](https://github.com/adrijshikhar): destaque visual do calendário
  junto a uma apresentação profissional.
- [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg): uso de
  um SVG autocontido como imagem no perfil.

Sprites, alfabeto, composição e código desta fase foram desenhados para este
perfil. Nenhuma arte, personagem, áudio ou marca da Nintendo foi reutilizada.
