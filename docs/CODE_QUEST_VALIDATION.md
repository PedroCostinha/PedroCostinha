# Validação — CODE QUEST V2

Revisão local em **23/10/2026**, exclusivamente em `PedroCostinha/PedroCostinha`,
branch `feat/code-quest-v2`. Nenhum commit, push, PR ou merge realizado.

## Referência e preservação

- V1: 19 testes e `--check` aprovados antes das mudanças.
- Estado inicial: `feat/code-quest`, HEAD `7d91f76`, README modificado e
  `assets/profile/` não rastreado. A V2 parte desse mesmo HEAD.
- Após `git fetch origin`, `origin/main` (`4bd5629`) tem três commits adicionais.
  As diferenças de conteúdo eram apenas calendário e SVG. Não houve merge.
- Calendário final lido desse commit remoto: `github-graphql`, **369 dias,
  53 semanas, 261 contribuições**, de **19/10/2025 a 22/10/2026**. Sem nova consulta
  GraphQL local e sem dados simulados nos artefatos finais.
- README alterado apenas entre os delimitadores CODE QUEST. Restante e banners
  anteriores conferidos por SHA-256 contra o estado inicial.

## V1 e V2

| Aspecto | V1 local | V2 |
| --- | --- | --- |
| Percurso | Patamares separados, grupos de quatro semanas | Borda do calendário, fundações e grupos de seis semanas |
| Integração | Alturas por atividade | Alturas, contornos semanais sincronizados e destaque do dia da moeda |
| Explorador | 40 px, quatro quadros de corrida, dez poses | 42 px, seis quadros de corrida, quinze poses e braços articulados |
| Movimento | Velocidade constante desde a partida | Aceleração inicial, subida/ápice/queda e pousos com folga corporal |
| Moedas | Centro do patamar | Semana de um dia real de nível 3/4; coleta e contador no mesmo instante |
| Ambiente | Uma camada urbana | Duas camadas, luz vermelha, nuvens com relevo e parallax discreto |
| Movimento reduzido | CSS dentro do SVG | CSS e fonte estática explícita no picture do README |
| Ciclo | 20,8 s | 20,8 s; reposição do personagem oculta pelo fade |
| SVG animado | 218.215 bytes | 219.695 bytes; limite de 250.000 mantido |

## Testes e geração

Executados com **Python 3.12.14** do runtime disponível no Codex:

```sh
python -m unittest discover -s tests -v
python scripts/generate_code_quest.py --calendar assets/code-quest/calendar.json
python scripts/generate_code_quest.py --check
```

**32 testes aprovados**: 19 originais e 13 novos. Cobertura adicional: dimensões,
quadros distintos, toda a largura de 35 px contra plataformas, calendário intacto,
inversão da trajetória acelerada, elevação por dados, passagem pelas semanas,
coleta em calendários esparsos, contador sincronizado, ápice/pouso, conclusão e
reinício, composição estática, dados reais e orçamento com 54 semanas ativas.

As verificações identificaram e corrigiram colisão no salto inicial em atividade
máxima, tamanho excessivo no caso de 54 semanas e moeda omitida junto à borda.
A geração repetida não modifica artefatos. Os dois SVGs preservam todos os dias,
passam na validação XML/referências e não dependem de scripts ou recursos externos.
O estático tem **168.691 bytes**, sem `@keyframes`. O PNG registra 18,3 s; não é
atualizado pelo workflow e não deve ser usado para consultar totais futuros.

## Inspeção visual realizada

Chrome **155.0.8059.85**, headless, renderização real por Playwright:

- Capturas: introdução (0,65 s), início (2 s), primeiro salto (~2,30 s), coleta
  (~15,65 s), meio (9,1 s), bandeira (17,2 s), vitória (18,3 s), reinício (20,6 s).
- Comparação V1/V2 em 9,1 s. A V1 tinha 256 contribuições; a mudança para 261
  vem dos dados remotos, não de uma alteração visual ou fabricação de contagens.
- SVG externo dentro de `<img>` em página local: capturas em instantes distintos
  confirmaram deslocamento, mudança de pose e contornos acompanhando as semanas.
- Versão animada em 360 e 768 px também inspecionada durante salto/corrida.
- `<picture>` em **360×156, 768×333 e 1200×520**: carregamento completo, proporção
  preservada e fonte estática selecionada em movimento reduzido (`currentSrc`).
- SVG direto com preferência reduzida: **zero animações ativas**, personagem em
  `(1116, 312)`, calendário completo e mensagem de vitória.
- A emulação de movimento reduzido não se propagou ao SVG animado em `<img>`
  no ambiente testado. A fonte alternativa explícita corrige esse caso no README;
  seleção e capturas foram conferidas. O SVG direto respeita a preferência.
- Sem erros de página registrados. JavaScript usado apenas no equipamento de
  captura, nunca dentro dos SVGs publicados.

Capturas, metadados e harness local: `.git/code-quest-v2-review/`, fora dos arquivos
a versionar. Prévia principal: `assets/code-quest/preview.png`.

## Workflow

Preservados GraphQL, `GITHUB_TOKEN`, tentativas/erros, permissões, concorrência,
Python 3.12, publicação condicionada a diff e cron `17 8 * * *` (05h17 Brasília).

Sintaxe YAML analisada; cron, gatilhos e permissões conferidos.
Tags/SHAs e metadados conferidos nas fontes oficiais:

- `checkout v7.0.1`: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `setup-python v7.1.0`: `6d4fd22b20465ccc0f7354476588e8df7c9ca0e0`.
- Ambas declaram Node 24. Runner mínimo documentado: 2.327.1; o fluxo usa runner
  hospedado, sem checkout em contêiner ou gatilhos privilegiados.
- `ubuntu-24.04` fixa o ambiente conhecido durante a migração de `ubuntu-latest`
  para 26.04, anunciada para 19/10–19/11/2026.
- Único acréscimo na publicação: SVG estático, gerado/validado junto com o animado.
  Não há etapa que execute commits incondicionais.

Fontes oficiais: [checkout](https://github.com/actions/checkout/releases/tag/v7.0.1),
[setup-python](https://github.com/actions/setup-python/releases/tag/v7.1.0),
[retirada do Node 20](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/),
[migração Ubuntu](https://github.blog/changelog/2026-09-17-ubuntu-26-generally-available-and-latest-migration/).

## Arquivos alterados por esta revisão

- `scripts/code_quest/motion.py`, `sprites.py`, `scene.py`: geometria, arte e cena.
- `scripts/generate_code_quest.py`: geração e conferência dos dois SVGs.
- `tests/test_code_quest.py`: 13 testes adicionais.
- `assets/code-quest/calendar.json`: snapshot real de origin/main.
- `assets/code-quest/code-quest.svg`, `preview.png`: animação e fotograma V2.
- `assets/code-quest/code-quest-static.svg`: novo, mesma cena/dados sem movimento.
- `.github/workflows/update-code-quest.yml`: Actions, runner e publicação do estático.
- `README.md`: somente integração com picture na seção CODE QUEST.
- `docs/CODE_QUEST.md` e este registro: comportamento e evidências atualizados.

## Limitações

A V2 **não foi publicada nem executada no GitHub Actions**. A renderização no
README hospedado pelo GitHub/Camo ainda precisa ser conferida depois de publicação
autorizada. Os testes locais não certificam sanitização/cache remotos.

Sem teste independente em Firefox, Safari/iOS, Edge ou dispositivos físicos.
Larguras móveis emuladas no Chrome. Em 360 px, textos secundários e detalhes do
sprite ficam pequenos; o calendário anual permanece completo e a imagem é ligada
ao SVG integral. O calendário final é de 22/10, não uma consulta atualizada até 23/10.

Este registro substitui o relatório inicial que ainda dizia que a publicação da
V1 estava impedida. A V1 já foi publicada pelo usuário; esta revisão não alega
ter validado sua renderização remota.
