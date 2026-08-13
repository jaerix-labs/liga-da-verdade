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
- **Não analisa toda a Liga.** Só os jogos dos quatro grandes.
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
taxa média de golos por minuto da Liga. Determinística: o mesmo lance dá sempre
exatamente o mesmo número.

### Erros que não produzem um estado certo

Quando não se sabe o que teria acontecido (penálti por marcar, ocasião
interrompida), o mundo corrigido é uma **mistura ponderada de dois estados**:

`valor = p × (estado com golo) + (1 − p) × (estado sem golo)`

`p` é o único número a estimar, e vem de estatística pública (xG), não de
opinião.

### Catálogo de famílias

| # | Família | Como se calcula |
|---|---------|-----------------|
| 1 | Golo validado indevidamente | Estado real (com golo) vs. estado sem golo |
| 2 | Golo anulado indevidamente | Simétrico do anterior |
| 3 | Golo nascido de decisão errada anterior | Mundo corrigido = o que o analista diz que devia ter acontecido (pontapé de baliza, canto, livre), com o `p` correspondente |
| 4 | Grande penalidade por assinalar | Mistura com `p` = taxa de conversão de penáltis |
| 5 | Penálti mal assinalado e falhado | Regista-se; impacto 0 |
| 6 | Ocasião de golo interrompida por decisão errada | Mistura com `p` por escalão (ver abaixo) |
| 7 | Expulsão indevida ou por mostrar | Estado corrigido tem 11 jogadores em vez de 10, nos minutos que faltavam |
| 8 | Cartão amarelo indevido | Regista-se; impacto 0 na v1 |

**Fora do catálogo, sem registo:** tempo de compensação (D18), estado do
relvado, e tudo o que não seja uma decisão de arbitragem sobre um lance.

### Escalões da família 6

**Quem classifica o escalão é o analista, pelas palavras que usou.** O João
transcreve, não julga.

| Escalão | Descrição típica do analista |
|---------|------------------------------|
| Isolado com o guarda-redes | "ficava isolado", "cara a cara" |
| Remate claro na área | "em zona de finalização", "boa posição de remate" |
| Ataque sem finalização iminente | tudo o resto |

**Se a descrição não chegar, aplica-se o escalão mais baixo.** A dúvida nunca
joga a favor de ninguém.

### Duas propriedades verificadas

- Um penálti inventado pesa **mais** aos 88' do que aos 2'. Corrigiu a intuição
  inicial do João: aos 2 minutos o adversário ainda tem 88 para responder.
- Uma expulsão pesa **muito mais** aos 10' do que aos 85'. Confirmou a intuição
  inicial do João.

### Cálculo por equipa

Em jogos entre dois dos quatro grandes, calcular os pontos esperados de **cada
equipa separadamente** nos dois mundos. Com empates possíveis, o ganho de uma
não é o simétrico da perda da outra.

### Da soma à tabela

`pontos Liga da Verdade = pontos reais − impactos a favor + impactos contra`

### Parâmetros

Meia dúzia, **todos publicados no site**, todos medíveis em dados públicos.
**Selados antes da jornada 1 e imutáveis durante a época.**

---

## 7. REGRAS DE RECOLHA

- **Âmbito**: todos os jogos dos quatro grandes (Benfica, FC Porto, Sporting,
  Sp. Braga) na época 2026/27. Cerca de 124 jogos.
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
2. **Formato dos dados.** `dados/2026-27.json` + 2-3 incidentes reais da
   jornada 1 como teste. **EM CURSO.**
3. **Liga real.** Ler o JSON e desenhar a classificação oficial.
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

- **[SUPOSIÇÃO] Valores de `p`.** Taxa de conversão de penáltis (~0,76) e os
  `p` dos escalões da família 6 (~0,35 / ~0,15 / ~0,03) são estimativas.
  **Verificar contra fontes públicas de xG e apresentar ao João com origem,
  antes de selar.** É a primeira coisa a fechar antes do entregável 4.
- **[SUPOSIÇÃO] Taxa média de golos por minuto e efeito de jogar com dez** na I
  Liga. A confirmar em dados públicos.
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

- Só se analisam jogos dos quatro grandes.
- Os analistas escolhem os lances que comentam. O conjunto registado está
  naturalmente inclinado para o erro, e para os clubes cujos adeptos mais
  reclamam.
- Um lance sustentado por uma só opinião vale tanto no cálculo como um
  sustentado por sete. O número de opiniões está sempre à vista.
- O painel não é equilibrado por jornal: Record 3 analistas, O Jogo 3, A Bola
  1.
- A cobertura não é igual entre jogos: os clássicos recebem mais atenção.
- Cartões amarelos e tempo de compensação não entram no cálculo.
- Todas as equipas são tratadas como iguais em força.
- O modelo tem escolhas discutíveis. **Não é irrefutável, e não se apresenta
  como tal.** O que oferece é que quem discorde tem de discordar de um número
  publicado, e não de uma pessoa.

---

## 15. BUGS CORRIGIDOS E AVISOS PARA NÃO DESFAZER

*(Vazio. Preencher à medida que aparecerem, com a causa e um aviso explícito
para não reverter a correção.)*
