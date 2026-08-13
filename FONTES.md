# FONTES.md — Liga da Verdade

Biblioteca de fontes e rotina de recolha. Companheiro do CLAUDE.md.
Atualizado em 2026-08-13.

**Regra que manda em tudo:** esta lista fechou antes da contagem começar e
**não muda durante a época 2026/27**. Se a meio da época uma fonte der
resultados inconvenientes, fica na mesma. O histórico do Git mostraria
qualquer troca, com data.

**A lista é de pessoas, não de cabeçalhos de jornal.** Um analista que escreva
em dois sítios conta uma vez.

---

## 1. A LISTA FECHADA — 7 ANALISTAS

| # | Analista | Jornal | Rubrica | Quando sai |
|---|----------|--------|---------|------------|
| 1 | Pedro Henriques | A Bola | *O árbitro de A BOLA* | Domingo |
| 2 | Jorge Faustino | Record | *Casos R* | Domingo |
| 3 | Marco Ferreira | Record | *Casos R* | Domingo |
| 4 | Iturralde González | Record | *Liga da Verdade* | Terça |
| 5 | Jorge Coroado | O Jogo | *Tribunal O JOGO* | Domingo |
| 6 | José Leirós | O Jogo | *Tribunal O JOGO* | Domingo |
| 7 | Fortunato Azevedo | O Jogo | *Tribunal O JOGO* | Domingo |

### Porque é que este painel é defensável

- **Três donos diferentes.** Record (Medialivre), O Jogo (grupo do Jornal de
  Notícias), A Bola (grupo suíço Ringier). Não é o painel de uma redação só,
  nem escolhido pelo João.
- **Todos são ex-árbitros.** Não entram comentadores desportivos genéricos.
- **Um estrangeiro.** Iturralde González, antigo árbitro internacional
  espanhol, sem histórico no futebol português nem ligação a nenhum clube. É a
  opinião menos atacável do conjunto.

### Assimetria a declarar no site

O Record traz 3 analistas, O Jogo traz 3, A Bola traz 1. Não é problema — é
consequência de contarmos pessoas e não jornais — mas tem de estar escrito na
página de método, para ninguém dizer que foi arranjado.

---

## 2. ACESSO

### Via principal: PressReader (subscrito pelo João)

Dá a edição impressa dos três jornais, tal como sai para as bancas. **Cobre o
painel todo numa só rotina**, em vez de andar à pesca em três sites. É onde
vivem as quatro rubricas da tabela acima — todas são páginas de jornal
impresso.

Em curso: tentar obter conta de biblioteca municipal com PressReader (a do
município do João não serve). Se resultar, o custo cai a zero.

### Via alternativa: A Bola online, gratuito e completo

A análise do Pedro Henriques é publicada **na íntegra e sem paywall** em
abola.pt, cerca das 09:30 do dia seguinte ao jogo, com todos os lances e os
mesmos textos da edição em papel.

Página de autor (lista tudo o que ele publica, por ordem):
`https://www.abola.pt/autor/pedro-henriques-2025050217292998075`

### Via alternativa: O Jogo online

Página de tópico com todas as peças do *Tribunal*:
`https://www.ojogo.pt/topico/tribunal-o-jogo`

Secção mais abrangente:
`https://www.ojogo.pt/topico/arbitragem`

**Ressalva:** algumas peças aparecem marcadas como *Exclusivo* e podem estar
fechadas. Muitas outras estão abertas com o painel completo.

### Via alternativa: Observador — Pedro Henriques

Secção de arbitragem de acesso livre e podcast *Sem Falta*, com transcrição
publicada.

`https://observador.pt/seccao/desporto/arbitragem/`

**É o mesmo analista d'A Bola.** Serve só como recurso quando o jornal falhar.
**Nunca conta como voto adicional.**

### Última linha: compra avulsa

Legítima. Um exemplar comprado é fonte citável com jornal, data e página.

---

## 3. EXCLUÍDOS, E PORQUÊ

| Fonte | Razão |
|-------|-------|
| **Canal 11** | Pertence à FPF, que tutela a arbitragem |
| **Canais de clube** (Benfica TV, Porto Canal, Sporting TV) | Óbvio |
| **CMTV** — *Pé em Riste*, *Liga D'Ouro* | Painéis com comentadores afetos aos clubes. É o ruído que o projeto quer medir, não a régua para o medir |
| **Apreciações do Conselho de Arbitragem** | Avaliam o árbitro em bloco («satisfatório», «insatisfatório»), não lance a lance. Não servem ao modelo |
| **Comentadores sem carreira de arbitragem** | A lista é de ex-árbitros |
| **Grupos de Telegram/WhatsApp com jornais** | Ilegal, e destruiria a rastreabilidade que é a razão de ser do projeto |

---

## 4. ROTINA SEMANAL

| Quando | O quê |
|--------|-------|
| Domingo / segunda | PressReader: A Bola (*O árbitro de A BOLA*), Record (*Casos R*), O Jogo (*Tribunal*) |
| Terça | PressReader: Record (*Liga da Verdade*, Iturralde) |
| Se o PressReader falhar | abola.pt (página de autor) e ojogo.pt (página de tópico) |
| Uma vez por semana | Guardar provas em `Provas-LigaDaVerdade/2026-27/JXX/` e registar os lances |

### Convenção de nomes das provas

```
Provas-LigaDaVerdade/
  2026-27/
    J01/
      J01_2026-08-09_abola_henriques.jpeg
      J01_2026-08-09_record_faustino_ferreira.jpeg
      J01_2026-08-09_ojogo_coroado_leiros_azevedo.jpeg
      J01_2026-08-12_record_iturralde.jpg
```

`JXX_AAAA-MM-DD_fonte_analista(s).ext` — a data é a de **publicação**, não a do
jogo. Uma peça cobre frequentemente vários jogos (a do Iturralde cobre três);
por isso o arquivo organiza-se por publicação, e a ligação ao jogo faz-se no
JSON.

---

## 5. O QUE APRENDEMOS COM A JORNADA 1

Ensaio real sobre o Estrela da Amadora-Sporting (2-2), com os quatro recortes.

### O formato de cada fonte

| Fonte | Formato |
|-------|---------|
| A Bola | Texto corrido por minuto, com ✔/✘. **O jogo inteiro** — 10 lances |
| Record *Casos R* | Blocos por lance, selo CERTO/ERRADO por analista. 5 lances |
| Record *Iturralde* | Lances numerados, **vários jogos na mesma peça**. 3 lances deste jogo |
| O Jogo *Tribunal* | **Matriz: pergunta por lance × 3 analistas, com seta verde/vermelha.** 5 lances |

**O *Tribunal* d'O Jogo é o formato-âncora.** É exatamente a estrutura de que o
projeto precisa. A lista de lances de cada jogo começa por ser a lista de
perguntas do *Tribunal*; as outras fontes encaixam por cima.

### A nota do árbitro ignora-se

O Record dá nota ao árbitro; A Bola também. **Não interessa.** Avalia-se se o
árbitro acertou ou não acertou em cada lance.

### O mesmo lance pode aparecer com minutos diferentes

Neste jogo: A Bola ancorou na falta (71'), Record e O Jogo ancoraram no golo
(72'). Nenhum errou — são momentos diferentes da mesma jogada. Ver a regra do
identificador no CLAUDE.md, secção 7.

### A maioria dos lances tem impacto zero

Dos 10 lances comentados neste jogo, **8 não mexem na tabela**: decisões
corretas, um amarelo por mostrar, tempo de compensação. Só dois têm impacto —
o segundo amarelo por mostrar aos 67' e o golo validado aos 71'-72'.

**Boa notícia para o esforço:** registas tudo, o motor calcula pouco.

---

## 6. RISCOS E COISAS POR VIGIAR

- **[VIGIAR] Cobertura desigual entre jogos.** O Iturralde escolhe 3-4 lances
  de toda a jornada; o *Tribunal* faz 5 perguntas de um jogo; o Henriques faz o
  jogo inteiro. Um Braga-Arouca vai ter menos atenção do que um clássico —
  logo, denominadores mais pequenos e opiniões isoladas a valer 100%. **Medir
  nas primeiras 3-4 jornadas: quantos analistas cobriram cada jogo.**
- **[VIGIAR] O painel pode mudar a meio da época.** Se um analista sair ou
  entrar, registar a data e **não recalcular o passado**. Nunca substituir um
  analista por outro a meio.
- **[VIGIAR] Peças d'O Jogo marcadas como *Exclusivo*** podem estar fechadas
  online. O PressReader resolve.
- **[FORA DA LISTA] Duarte Gomes.** Foi Diretor Técnico Nacional de Arbitragem
  e há indicação de demissão em julho de 2026, em contexto de polémica.
  Duplamente problemático: pode não estar a comentar, e pode ter deixado de ser
  visto como imparcial.

---

## 7. O QUE NUNCA ENTRA NO REPOSITÓRIO

Imagens, recortes, PDFs ou texto integral de jornais. O repositório é público.
Guarda-se a **citação** — jornal, data, página, analista, ligação — e a imagem
fica na pasta de provas, fora do Git.
