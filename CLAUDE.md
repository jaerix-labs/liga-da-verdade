# CLAUDE.md — Liga da Verdade

Este ficheiro é a memória do projeto. Qualquer conversa nova lê-o ao abrir,
antes de fazer seja o que for. Está escrito para que o João possa mudar de
computador e de sessão sem re-explicar nada.

**Ler também o `FONTES.md`**, que contém a lista fechada de analistas, as vias
de acesso e a rotina de recolha.

Última atualização: 2026-08-13

---

## 1. QUEM É O JOÃO E COMO TRABALHAMOS

O João não é programador. É estudante de mestrado em Ciência de Dados e
trabalha em logística hospitalar. Todo o código é escrito e mantido pelo
Claude.

- Falar sempre em **português europeu**, sem jargão desnecessário. Quando um
  termo técnico for inevitável, explicá-lo na primeira vez que aparece.
- O João trabalha em mais do que um computador e dedica **pouco tempo de cada
  vez** ao projeto.

### Regras de processo (valem para toda a vida da app)

1. **PLANO ANTES DE CÓDIGO.** Antes de escrever código para um entregável
   novo, apresentar o plano e esperar por aprovação explícita.
2. **ENTREGÁVEIS PEQUENOS, UM DE CADA VEZ.** O João testa cada um no browser
   antes de se avançar para o seguinte.
3. **UM PEDIDO, UMA ALTERAÇÃO.** Perante um pedido vago, pedir para
   concretizar em vez de adivinhar.
4. **.GITIGNORE ANTES DO PRIMEIRO COMMIT.** Feito. Nunca correr `git add .` às
   cegas: correr `git status` antes e confirmar o que vai entrar.
5. **ESTE FICHEIRO É A MEMÓRIA.** Atualizar sempre que se tome uma decisão
   estrutural ou se corrija um bug cuja causa não era óbvia. Nesse caso,
   escrever também a explicação e um aviso para não desfazer a correção.
6. **CONTRADIÇÕES AVISAM-SE.** Se o João pedir algo que contradiga este
   ficheiro, avisar em vez de assumir que ele mudou de ideias.
7. **ERROS COLAM-SE INTEIROS.** Quando algo falhar, dar instruções para o João
   colar o erro completo. Nunca pedir que descreva o sintoma.

---

## 2. O QUE A APP FAZ

Uma app pública que calcula, de forma auditável, quem foi beneficiado e quem
foi prejudicado pela arbitragem na I Liga portuguesa, e publica duas tabelas
lado a lado:

- **Liga real** — a classificação oficial.
- **Liga da Verdade** — a classificação corrigida do impacto dos erros de
  arbitragem, em pontos decimais.

A app não emite juízos próprios sobre os lances. Transcreve as opiniões de
analistas de arbitragem publicadas na imprensa e converte-as em pontos através
de um modelo fixo, publicado e igual para todos.

## 3. O QUE A APP NÃO FAZ

- **Não avalia lances.** O Claude e o João nunca decidem se houve erro. Só
  analistas publicados o fazem.
- **Não decide que lances existem.** Um lance entra se e só se pelo menos um
  analista da lista o comentou.
- **Não avalia árbitros.** As notas globais que os jornais dão aos árbitros são
  ignoradas. Interessa o lance, não o árbitro.
- **Não republica conteúdo de jornais.** Só citação e ligação.
- **Não analisa toda a Liga.** Só os jogos dos três grandes (Benfica, FC Porto,
  Sporting). Ver D22.
- **Não contabiliza cartões amarelos nem tempo de compensação.**
- **Não modela a força individual das equipas** (v1).
- **Não usa Excel, nem cloud privada, nem caminhos para ficheiros externos.**
  Ver secção 4 e D21.

---

## 4. ARQUITETURA — **FECHADA, NÃO REABRIR SEM PEDIDO EXPLÍCITO DO JOÃO**

### Base

- **Um único `index.html` autossuficiente**: HTML + CSS + JavaScript vanilla.
  Sem passo de build, sem framework, sem npm, sem `node_modules`.
- **ZERO CDN.** Nada carregado de servidores de terceiros: nem bibliotecas, nem
  tipos de letra, nem ícones. Tudo dentro do próprio ficheiro.
- **Alojamento: GitHub Pages, repositório PÚBLICO.** A auditabilidade é a razão
  de ser do projeto, por isso o repositório público é requisito e não
  concessão.
- **`servidor.bat`** que arranca um servidor local em Python e abre o browser.
  **Obrigatório:** a app lê o JSON com `fetch()`, que falha se o `index.html`
  for aberto diretamente do disco.

### Estado atual do alojamento

- Repositório: `jaerix-labs/liga-da-verdade` (público)
- Site: `https://jaerix-labs.github.io/liga-da-verdade/`
- GitHub Pages ativo a partir do branch `main`, pasta raiz

### Dados

- Os dados vivem em **`dados/2026-27.json`, dentro do repositório**, lidos com
  `fetch()` da mesma origem. Qualquer pessoa abre o site em qualquer browser,
  incluindo telemóvel, e vê tudo sem fazer nada.
- **Uma época, um ficheiro.** 2027/28 será `dados/2027-28.json`, análise
  independente. Nunca se misturam épocas.
- **JSON, nunca Excel.** Ler Excel no browser exigiria biblioteca externa
  (viola zero CDN) e o Git não mostra o que muda dentro de um binário, o que
  destrói a auditabilidade.
- **O Git substitui a cloud** como forma de os dados viajarem entre
  computadores. Rotina: `git pull` ao chegar, `git push` ao sair.

### Modo de edição

- Ativado por `?admin=1`. É o **único** sítio onde se usa a File System Access
  API — `showDirectoryPicker()`, apontada à **pasta do repositório clonado**,
  nunca a uma pasta cloud arbitrária.
- Guardar a referência em IndexedDB. Ao reabrir, mostrar a pasta memorizada e
  pedir só confirmação de acesso. Botões para trocar e para esquecer.
- **Degradação obrigatória:** detetar se a API existe antes de a usar. Onde não
  existir (Firefox, Safari, qualquer telemóvel), avisar com mensagem clara e
  oferecer **descarregar** o JSON alterado, com aviso explícito de que não
  substitui o original. Nunca deixar parecer que gravou quando não gravou.
  **Testar este caminho, não só o principal.**
- Antes de gravar, reler o ficheiro em disco e avisar se mudou entretanto.

### Preferências e segredos

- Preferências de interface no `localStorage`.
- **Não há segredos neste projeto.** Nenhuma chave de API, nenhuma conta de
  serviço. Se alguma vez for preciso, nunca vai no código.

### Ficheiros que NUNCA entram no repositório

Imagens e recortes de jornais, configuração local, pasta `.claude`.

---

## 5. REGRA DE COMMIT E PUSH

**O site online só muda depois de `git push`.**

- **Nunca dizer ao João para testar "no link" sem ter feito commit e push
  antes.**
- Assim que o João testar e disser que funciona e que gosta, fazer commit com
  mensagem descritiva e push **automaticamente**, sem voltar a pedir
  confirmação. Isto substitui qualquer regra mais cautelosa de commits.
- Esta autorização aplica-se **só ao push do código**. Mexer em definições de
  alojamento, contas ou plataformas exige sempre explicar os passos primeiro.

---

## 6. O MODELO DE CÁLCULO — "O TERMÓMETRO"

### O princípio único

Existe **uma só regra**, aplicada a todos os tipos de erro sem exceção:

> Quantos pontos esperava esta equipa fazer neste jogo, no instante anterior ao
> lance — e quantos esperaria se o árbitro tivesse acertado?

A diferença entre os dois números é o impacto, em pontos decimais. Não há
tabela de pesos por tipo de lance.

### Estado de jogo

Um estado é `(minuto, resultado, jogadores em campo de cada lado)`. A cada
estado corresponde um valor em **pontos esperados**:

`pontos esperados = 3 × P(vitória) + 1 × P(empate)`

As probabilidades saem de uma simulação simples do tempo que falta, a partir da
taxa média de golos por minuto da Liga — **uma taxa para quem joga em casa,
outra para quem joga fora** (D27). Determinística: o mesmo lance dá sempre
exatamente o mesmo número.

### Erros que não produzem um estado certo

Quando não se sabe o que teria acontecido (penálti por marcar, ocasião
interrompida), o mundo corrigido é uma **mistura ponderada de dois estados**:

`valor = p × (estado com golo) + (1 − p) × (estado sem golo)`

`p` é o único número a estimar, e vem de estatística pública (xG), não de
opinião.

### Catálogo de famílias

| # | Família | Tipo(s) no JSON | Como se calcula |
|---|---------|------------------|-----------------|
| 1 | Golo validado indevidamente | `golo_validado` | Estado real (com golo) vs. estado sem golo |
| 2 | Golo anulado indevidamente | `golo_anulado` | Simétrico do anterior |
| 3 | Golo nascido de decisão errada anterior | `golo_apos_decisao_anterior`; `penalti_assinalado` (se convertido) | Mundo corrigido = o que o analista diz que devia ter acontecido (pontapé de baliza, canto, livre, **ou a atribuição do reinício — canto vs. lateral vs. pontapé de baliza**), com o `p` correspondente |
| 4 | Grande penalidade por assinalar | `penalti_nao_assinalado` | Mistura com `p` = taxa de conversão de penáltis |
| 5 | Penálti mal assinalado e falhado | `penalti_assinalado` (se falhado) | Regista-se; impacto 0 |
| 6 | Ocasião de golo interrompida por decisão errada | `ocasiao_interrompida` (exige `escalao`) | Mistura com `p` por escalão (ver abaixo). Inclui travar a jogada por um reinício mal atribuído (canto, lateral, pontapé de baliza), não só falta/fora de jogo fantasma |
| 7 | Expulsão indevida ou por mostrar | `expulsao_nao_mostrada`; `expulsao_mostrada` | Estado corrigido tem 11 jogadores em vez de 10, nos minutos que faltavam |
| 8 | Cartão amarelo indevido | `amarelo_mostrado`; `amarelo_nao_mostrado` | Regista-se; impacto 0 na v1 |

**Fora do catálogo, sem registo:** tempo de compensação (D18), estado do
relvado, e tudo o que não seja uma decisão de arbitragem sobre um lance.

### Vocabulário fechado de "tipo" — e como se deriva a família

O JSON **não guarda "familia"**. Guarda `tipo` (um destes dez valores, fechado
— não se acrescentam novos sem rever este catálogo) e a família deriva-se dele
em código, no Entregável 4, por uma tabela fixa: a da tabela acima.

`golo_validado` | `golo_anulado` | `golo_apos_decisao_anterior` |
`penalti_assinalado` | `penalti_nao_assinalado` | `ocasiao_interrompida` |
`expulsao_mostrada` | `expulsao_nao_mostrada` | `amarelo_mostrado` |
`amarelo_nao_mostrado`

**Princípio 1 (D23): a família deriva do `tipo` mais os factos do jogo que já
estão no ficheiro. Nunca de uma inferência nova.** O único caso em que um
`tipo` sozinho não chega é `penalti_assinalado` (família 3 se convertido,
família 5 se falhado) — e mesmo aí não se infere nada: o bloco `golos` do jogo
já diz se houve golo, e `incidente_relacionado` já liga o golo ao incidente. A
distinção lê-se, não se adivinha.

**Princípio 2 (D24): o `tipo` descreve o que o árbitro fez, nunca se
acertou.** Por isso vem em pares — `_mostrado`/`_nao_mostrado`,
`assinalado`/`nao_assinalado` — cada um servindo tanto para a decisão certa
como para a errada. A família só entra em jogo (só há impacto a calcular)
**quando o veredicto é `errado`.** Com `certo`, o impacto é zero, seja qual for
o tipo — o `tipo` não é, e nunca foi, um juízo sobre o lance; isso continua a
ser só dos analistas.

**Se aparecer um lance cujo `tipo` não couber neste vocabulário, o programa
para e avisa o João** — não se inventa um tipo novo em código. Significa que o
catálogo das oito famílias tem uma lacuna, e isso discute-se antes de se
resolver.

### Regra do VAR (D25)

**Regista-se sempre a decisão final** — a que ficou em vigor no jogo, depois
de qualquer revisão.

- Um erro assinalado no relvado e **corrigido pelo VAR antes de produzir
  consequências** não é um incidente com impacto a medir. É contexto, e vai
  na descrição do lance — não gera `tipo` próprio nem entra na conta.
- **Se um analista disser que a própria correção do VAR estava errada**, aí
  sim há erro a medir, e o mundo corrigido é o que esse analista defende.
- **O minuto do incidente é o do lance, nunca o do golo que vier a seguir**,
  mesmo quando a revisão do VAR atrasa esse golo em vários minutos (ex.:
  penálti assinalado aos 5', golo aos 9' — o incidente regista-se aos 5', e o
  `resultado_antes` é o do minuto 5, não o do minuto 9).

### Escalões da família 6

**Quem classifica o escalão é o analista, pelas palavras que usou.** O João
transcreve, não julga.

| Escalão | Descrição típica do analista | `p` | Porquê |
|---------|------------------------------|-----|--------|
| Isolado com o guarda-redes | "ficava isolado", "cara a cara" | **0,35** | P(chegar ao remate) × xG do remate ≈ 0,6 × 0,6. Mesmo "isolado", falta ainda controlar a bola e rematar — o lance nunca chegou a acontecer |
| Remate claro na área | "em zona de finalização", "boa posição de remate" | **0,15** | xG médio de um remate dentro da área (~0,10-0,12), arredondado para cima por a descrição implicar posição acima da média. **Não** se usa o xG de "big chance" (~0,3) — isso é um caso particular, não a descrição genérica |
| Ataque sem finalização iminente | tudo o resto | **0,03** | Valor mais baixo, por defeito — não há remate nem posição descrita |

**Se a descrição não chegar, aplica-se o escalão mais baixo.** A dúvida nunca
joga a favor de ninguém.

### Duas propriedades verificadas

- Um penálti inventado pesa **mais** aos 88' do que aos 2'. Corrigiu a intuição
  inicial do João: aos 2 minutos o adversário ainda tem 88 para responder.
- Uma expulsão pesa **muito mais** aos 10' do que aos 85'. Confirmou a intuição
  inicial do João.

### Cálculo por equipa

Em jogos entre dois dos três grandes, calcular os pontos esperados de **cada
equipa separadamente** nos dois mundos. Com empates possíveis, o ganho de uma
não é o simétrico da perda da outra.

### Como se mede o impacto (D29)

**O impacto de um lance mede-se no instante desse lance** — compara-se o
estado real do jogo nesse minuto com o estado corrigido nesse mesmo minuto,
pela mesma simulação de pontos esperados. **Nunca se volta a simular o resto
do jogo real** a partir daí; o que aconteceu depois, aconteceu.

**Se um jogo tiver vários lances com impacto, cada um calcula-se
independentemente, contra o estado real no seu próprio minuto, e os impactos
somam-se.** Não há efeito cascata de um lance sobre o cálculo de outro no
mesmo jogo — cada erro é a sua própria pergunta contrafactual, isolada.

### Da soma à tabela

`pontos Liga da Verdade = pontos reais − impactos a favor + impactos contra`

### Parâmetros — selados em 2026-08-14

**Princípio (D26): na dúvida sobre um parâmetro, escolhe-se sempre o valor
mais baixo.** Subestimar um erro é seguro; sobrestimar infla a correção e dá
munição a quem queira desacreditar o projeto. Todos os valores abaixo seguem
este princípio quando a fonte pública dava uma gama, não um número único.

| Parâmetro | Valor | Fonte |
|---|---|---|
| Taxa de conversão de penáltis | **0,76** | Ligas europeias de topo, ~75-78% de conversão; xG médio de um penálti ~0,76-0,79 |
| Golos por minuto — equipa da casa | **0,0171** (1,54 golos/jogo ÷ 90) | Primeira Liga 2025/26: 821 golos em 306 jogos = 2,68 golos/jogo. Sem repartição casa/fora publicada para a Liga portuguesa; repartido pela proporção geral europeia de golos marcados em casa vs. fora (~1,35:1) |
| Golos por minuto — equipa de fora | **0,0127** (1,14 golos/jogo ÷ 90) | Idem |
| `p` — escalões da família 6 | 0,35 / 0,15 / 0,03 | Ver tabela de escalões acima |
| Efeito de jogar com dez — a marcar | **×0,70** | Estudo académico sobre expulsões em Mundiais (não é liga de clubes — ver aviso abaixo) |
| Efeito de jogar com dez — a sofrer | **×1,25** | Idem |

**Vantagem caseira (D27):** as taxas de golos por minuto são diferentes para
quem joga em casa e para quem joga fora. Isto **não contraria a D11** — a D11
proíbe modelar a força individual de cada clube (o que abriria o flanco a
"puseste o teu clube mais forte"); a vantagem caseira aplica-se por igual a
todas as equipas, consoante jogam em casa ou fora, e não favorece clube
nenhum.

**Aviso (D28) — o efeito de jogar com dez é o parâmetro mais fraco do
modelo.** O estudo de origem mede médias por jogo inteiro de equipas que
levaram um vermelho, incluindo os minutos em que ainda jogavam 11 contra 11
— isso dilui o efeito real (uma expulsão aos 80' não é o mesmo que jogar toda
a Liga em inferioridade). Os multiplicadores estão provavelmente **abaixo**
do efeito verdadeiro. Como subestimar é o lado seguro, o valor fica selado
assim mesmo, mas **isto tem de estar declarado na página de método**
(Entregável 6) como a fragilidade mais séria do modelo.

**Todos os parâmetros ficam publicados no site (página de método) com a
respetiva fonte, e são imutáveis durante a época 2026/27.**

---

## 7. REGRAS DE RECOLHA

- **Âmbito**: todos os jogos dos três grandes (Benfica, FC Porto, Sporting) na
  época 2026/27. Cerca de 96 jogos. O Sp. Braga foi retirado do âmbito — ver
  D22.
- **Regra de entrada**: um lance entra se e só se **pelo menos um analista da
  lista o comentou**. Sem exceções — nem quando parecer óbvio que houve erro
  num lance que ninguém comentou.
- **Duas gavetas**: certo / errado. Avalia-se se o árbitro acertou ou não
  acertou; a dificuldade do lance não conta. Se o analista escreve que o lance
  era complicado mas conclui que a decisão estava errada, entra como **errado**.
- **Denominador**: conta **só quem se pronunciou sobre aquele lance**. O
  silêncio não é voto.
- **Um analista conta uma vez**, escreva ele em um ou em três sítios.
- **Guardar a opinião de cada analista, nome a nome. NUNCA a fração já
  calculada.**
- **Registar também os "certos"**: fazem falta ao denominador.
- **Cada incidente guarda a citação**: jornal, data de publicação, página,
  analista, e ligação quando existir online.
- **O site mostra quantas opiniões sustentam cada lance.** Não altera o
  cálculo; deixa quem olha julgar por si.

### Identificador do lance

**O minuto identifica o lance, e quem o atribui é o João, ao registar.**

O identificador pode ser composto quando as fontes ancoram em momentos
diferentes da mesma jogada — por exemplo `71-72`, quando A Bola descreve a
falta aos 71' e o Record e O Jogo descrevem o golo aos 72'.

**O programa nunca junta opiniões sozinho.** Quem decide que duas opiniões são
sobre o mesmo lance é o João, no momento do registo. Mesma lógica da regra de
entrada: transcreve-se, não se deixa a máquina adivinhar.

### Fluxo de trabalho atual (até existir o entregável 7)

1. O João lê as opiniões nos jornais.
2. Diz-as ao Claude **em linguagem normal**, sem estrutura nenhuma.
3. O Claude escreve o `dados/2026-27.json`.
4. Commit + push; o site atualiza para todos.

O João **nunca** escreve JSON à mão. A partir do entregável 7, passa a usar um
formulário no próprio site.

### Arquivo de provas — FORA DO REPOSITÓRIO

Ver `FONTES.md`, secção 4, para a convenção de nomes.

---

## 8. FONTES

**A lista nominal fechada está no `FONTES.md`.** Resumo: 7 analistas — Pedro
Henriques (A Bola), Jorge Faustino, Marco Ferreira e Iturralde González
(Record), Jorge Coroado, José Leirós e Fortunato Azevedo (O Jogo).

Acesso principal: **PressReader**, subscrito pelo João. Vias alternativas
gratuitas: abola.pt, ojogo.pt, Observador.

**A lista não muda durante a época.**

---

## 9. ESTRUTURA DE FICHEIROS

```
liga-da-verdade/            (repositório público no GitHub)
  index.html                (tudo: HTML + CSS + JS, zero CDN)
  servidor.bat              (servidor local Python + abre o browser)
  .gitignore
  CLAUDE.md                 (este ficheiro)
  FONTES.md                 (lista de fontes e rotina de recolha)
  dados/
    2026-27.json            (incidentes + classificação oficial)
```

---

## 10. DECISÕES TOMADAS

Todas em **2026-08-13**, salvo indicação.

| # | Decisão | Razão |
|---|---------|-------|
| D1 | Dados em JSON dentro do repositório, lidos com `fetch()` | O João acede de vários dispositivos. A File System Access API não existe em browsers de telemóvel |
| D2 | File System Access API só no modo de edição (`?admin=1`) | Mantém a escrita em disco sem impedir que o site funcione noutros browsers |
| D3 | GitHub Pages, repositório público | A auditabilidade é a razão de ser do projeto |
| D4 | Git substitui a cloud nesta app | Sincroniza dados e código de uma vez, e recusa edições em conflito |
| D5 | Âmbito: todos os jogos dos 4 grandes (~124) | Só os clássicos enviesaria a tabela; a Liga toda é impossível de alimentar |
| D6 | Época 2026/27, jornada a jornada | Arrancou a 8-9 de agosto de 2026. Épocas futuras em ficheiros separados |
| D7 | Silêncio não é voto — conta só quem se pronunciou | Decisão do João, de olhos abertos. **Fragilidade conhecida**: um lance comentado por um único analista dá 1/1 = 100%. Mitigado por mostrar sempre o número de opiniões |
| D8 | Duas gavetas: certo / errado | É assim que os analistas se exprimem. Um terceiro estado obrigaria o João a classificar frases ambíguas |
| D9 | Regra de entrada: só entra o que um analista comentou | Tira ao João a decisão do que entra |
| D10 | Um princípio único de cálculo (pontos esperados) | Substitui pesos arbitrários por uma regra explicável numa frase |
| D11 | Todas as equipas iguais em força na v1 | Parâmetros de força dos 4 clubes avaliados abririam o flanco a "puseste o teu clube mais forte" |
| D12 | Amarelos registados mas com impacto 0 | O efeito existe mas é indireto; pô-lo em pontos seria inventar um número |
| D13 | Imagens de jornais fora do repositório | O repositório é público; republicar páginas de jornal é conteúdo protegido |
| D14 | Página de método é entregável de v1 | Se a tabela ficar pronta e a explicação não, **não se publica** |
| D15 | Manter o nome "Liga da Verdade" | É o termo que o público reconhece. Ver riscos na secção 12 |
| D16 | Lista nominal fechada em 7 analistas | Três jornais de três donos diferentes, todos ex-árbitros, um deles estrangeiro. Ver `FONTES.md` |
| D17 | O minuto identifica o lance, atribuído pelo João; pode ser composto (`71-72`) | Fontes diferentes ancoram em momentos diferentes da mesma jogada. Quem junta é o João, nunca o programa |
| D18 | Tempo de compensação não entra em lado nenhum | Não é uma decisão sobre um lance e não se converte em pontos |
| D19 | PressReader como via principal de acesso | Cobre os três jornais numa só rotina, legalmente. Conta de biblioteca em curso |
| D20 | `classificacao_oficial` é um instantâneo manual, atualizado por jornada | Reconstruí-la a partir dos 306 jogos seria muito trabalho de recolha para dados que existem prontos |
| D21 | Confirmada a rejeição de Excel + cloud privada | Levantada de novo pelo João a 13/08 e recusada: um browser não lê um caminho de cloud privada sem credenciais, e credenciais são segredos que o projeto não tem |
| D22 | Sp. Braga retirado do âmbito. Projeto passa de "quatro grandes" a "três grandes" (Benfica, FC Porto, Sporting) | Ao recolher os lances da jornada 1, o João verificou que nenhum dos 7 analistas do painel comentou o jogo do Sp. Braga. Em vez de manter no âmbito uma equipa estruturalmente sem cobertura, decidiu retirá-la. Substitui D5 quanto ao número de equipas e de jogos |
| D23 | O JSON não guarda "familia". Guarda um `tipo` de vocabulário fechado (dez valores) e a família deriva-se dele em código, no Entregável 4 | `familia` era redundante com `tipo` e nada garantia que os dois campos continuassem de acordo ao longo da época. Fechar o vocabulário de `tipo` agora evita ter de reclassificar lances de jornadas passadas quando aparecer um caso novo a meio da época. Princípio: a família deriva do `tipo` mais os factos do jogo já registados (ex.: se um `penalti_assinalado` teve golo, via o bloco `golos`), nunca de uma inferência nova |
| D24 | Vocabulário de `tipo` renomeado: `penalti_indevido` → `penalti_assinalado`, `expulsao_indevida` → `expulsao_mostrada`. O `tipo` descreve o que o árbitro fez, nunca se acertou; a família só se aplica quando o veredicto é `errado` | Ao recolher o jogo FC Porto-Alverca, apareceram dois penáltis corretamente assinalados. `penalti_indevido` já continha um juízo no próprio nome, o que contraria o princípio do projeto: quem julga são os analistas, o `tipo` só descreve a decisão |
| D25 | Regra do VAR: regista-se sempre a decisão final. Um erro corrigido pelo VAR antes de produzir consequências é contexto na descrição, não um incidente com impacto. O minuto do incidente é o do lance, não o do golo que vier depois da revisão | Apareceu no jogo FC Porto-Alverca (canto assinalado por engano e corrigido para pontapé de baliza; penáltis com golo alguns minutos depois da revisão do VAR) e vai repetir-se todas as semanas. Sem esta regra, o `resultado_antes` de um lance ficaria calculado com o resultado errado |
| D26 | Princípio: na dúvida sobre um parâmetro do modelo, escolhe-se sempre o valor mais baixo | Subestimar um erro é seguro; sobrestimar infla a correção e dá munição a quem queira desacreditar o projeto. Aplicado a todos os parâmetros selados (ver secção 6) |
| D27 | A taxa de golos por minuto é diferente para quem joga em casa e para quem joga fora | O modelo estava a dar a mesma taxa às duas equipas, o que punha o termómetro em 1,5-1,5 pontos esperados ao apito inicial — falso, a casa espera mais. **Não contraria a D11**: a vantagem caseira aplica-se por igual a todas as equipas, não modela a força de nenhum clube em particular |
| D28 | Efeito de jogar com dez selado em ×0,70 (a marcar) / ×1,25 (a sofrer), mas marcado como o parâmetro mais fraco do modelo | A fonte (estudo de Mundiais) mistura minutos em 11-contra-11 com minutos em inferioridade no mesmo número, diluindo o efeito real — os multiplicadores estão provavelmente abaixo do verdadeiro. Selado por D26 (subestimar é seguro), mas tem de estar declarado na página de método como fragilidade |
| D29 | O impacto de um lance mede-se no instante desse lance, contra o estado real nesse minuto — nunca se volta a simular o resto do jogo real. Vários lances no mesmo jogo somam-se independentemente | Precisava de estar escrito antes do motor de cálculo (Entregável 4), para não haver ambiguidade depois sobre como tratar jogos com mais do que um erro |

---

## 11. ALTERNATIVAS PONDERADAS E REJEITADAS

| Alternativa | Porque foi rejeitada |
|-------------|----------------------|
| Dados em Excel numa pasta cloud, lidos pela File System Access API | Não funciona em telemóvel; ler Excel exigiria biblioteca externa; o Git não mostra o que muda num binário; e o browser não acede a cloud privada sem segredos |
| Partilhar o Excel para os visitantes carregarem à mão | Circulariam versões desatualizadas |
| Netlify com repositório privado | O repositório privado retiraria a auditabilidade |
| Analisar só os jogos entre grandes | Corrigiria metade da tabela |
| Analisar a Liga toda | Ninguém avalia os jogos pequenos |
| Três gavetas (certo / duvidoso / errado) | Obrigaria o João a decidir se uma frase ambígua é "duvidoso" ou "errado" |
| Silêncio de quem viu o jogo = "não foi erro" | Recomendado pelo Claude, rejeitado pelo João |
| Força individual por equipa no modelo | Ver D11 |
| Canal 11 e canais de clube | Ver `FONTES.md`, secção 3 |
| Apreciações do Conselho de Arbitragem como voto | Avaliam o árbitro em bloco, não lance a lance |
| Duarte Gomes como analista | Ex-DTN de arbitragem, com indicação de demissão em polémica em julho de 2026 |
| Confirmação automática por proximidade de minutos | Proposta pelo Claude, rejeitada pelo João: o identificador composto resolve o caso |
| Grupos de Telegram/WhatsApp com jornais | Ilegal, e destruiria a rastreabilidade |

---

## 12. ENTREGÁVEIS DA V1, POR ORDEM

1. ~~**Esqueleto e publicação.**~~ **CONCLUÍDO.** Repositório, `.gitignore`,
   `index.html` mínimo, `servidor.bat`, GitHub Pages ativo.
2. ~~**Formato dos dados.**~~ **CONCLUÍDO.** `dados/2026-27.json` com a
   jornada 1 completa: 3 jogos (Estrela da Amadora-Sporting, FC Porto-Alverca,
   Benfica-Ac. Viseu), 34 lances reais e citados. Falta ainda a
   `classificacao_oficial` (totais das 18 equipas) para o Entregável 3.
3. ~~**Liga real.**~~ **CONCLUÍDO.** `index.html` lê o `dados/2026-27.json`
   com `fetch()` e desenha a classificação oficial (18 equipas), ordenada por
   `posicao`. Testado em desktop e telemóvel (375px), sem overflow horizontal.
4. **Motor de cálculo.** O termómetro, com testes visíveis em `?teste=1`,
   incluindo os dois casos de referência (penálti aos 2' vs. 88'; expulsão aos
   10' vs. 85').
5. **Liga da Verdade.** A tabela corrigida, com detalhe por lance.
6. **Página de método.** Regras, parâmetros, fontes, limitações. **Bloqueia a
   publicação se não estiver pronta.**
7. **Modo de edição** (`?admin=1`): formulário para registar um lance em menos
   de um minuto, escrita no JSON, com o caminho alternativo de download
   testado.
8. **Exportar dados em bruto** (CSV).

---

## 13. SUPOSIÇÕES E PONTOS POR CONFIRMAR

- ~~[SUPOSIÇÃO] Valores de `p`~~ **SELADO em 2026-08-14.** Ver secção 6,
  "Parâmetros" — penáltis 0,76; família 6 em 0,35/0,15/0,03, com justificação.
- ~~[SUPOSIÇÃO] Taxa média de golos por minuto e efeito de jogar com dez~~
  **SELADO em 2026-08-14.** Ver secção 6. **O efeito de jogar com dez fica
  marcado como o parâmetro mais fraco do modelo (D28)** — a fonte pública
  dilui o efeito real, e isto tem de estar na página de método.
- **[POR DECIDIR] A tabela mostra 18 equipas ou só 4?** Os clubes fora dos
  grandes só têm correções nos jogos contra eles. Se mostrar 18, a correção
  parcial tem de estar declarada em letra visível.
- **[POR DECIDIR] Como se apresenta a Liga da Verdade nas primeiras jornadas**,
  quando é quase igual à real.
- **[RISCO ACEITE] Nome "Liga da Verdade".** Antes de divulgar: consultar a
  base de marcas do INPI; não copiar o grafismo de nenhum jornal; pôr no rodapé
  que o site não tem ligação a nenhum jornal. **Isto não é aconselhamento
  jurídico.**

---

## 14. LIMITAÇÕES A DECLARAR NO PRÓPRIO SITE

Não são letra pequena. São parte do argumento.

- Só se analisam jogos dos três grandes (Benfica, FC Porto, Sporting). O Sp.
  Braga foi retirado do âmbito por não ter nenhuma cobertura do painel de
  analistas na jornada 1 (D22).
- Os analistas escolhem os lances que comentam. O conjunto registado está
  naturalmente inclinado para o erro, e para os clubes cujos adeptos mais
  reclamam.
- Um lance sustentado por uma só opinião vale tanto no cálculo como um
  sustentado por sete. O número de opiniões está sempre à vista.
- O painel não é equilibrado por jornal: Record 3 analistas, O Jogo 3, A Bola
  1.
- A cobertura não é igual entre jogos: os clássicos recebem mais atenção.
- Cartões amarelos e tempo de compensação não entram no cálculo.
- Todas as equipas são tratadas como iguais em força — só se modela a
  vantagem de jogar em casa (D27), igual para todos os clubes.
- **O efeito de jogar com dez em campo (D28) é o parâmetro mais fraco do
  modelo.** Vem de um estudo de Mundiais, não de liga de clubes, e a fonte
  mistura minutos em 11-contra-11 com minutos em inferioridade no mesmo
  número — o efeito real é provavelmente maior do que o valor usado.
- O modelo tem escolhas discutíveis. **Não é irrefutável, e não se apresenta
  como tal.** O que oferece é que quem discorde tem de discordar de um número
  publicado, e não de uma pessoa.

---

## 15. BUGS CORRIGIDOS E AVISOS PARA NÃO DESFAZER

*(Vazio. Preencher à medida que aparecerem, com a causa e um aviso explícito
para não reverter a correção.)*
