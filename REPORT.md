# Could Redbelly connect to Quant's Overledger?

A feasibility report for the Redbelly DAO community (TASK-29). Sources opened and read on 19, 20 and 21 October 2026.

This is feasibility research only. The sources reviewed (S1 to S5) do not mention Redbelly, and no source reviewed shows a partnership, talks or plans between Redbelly and Quant. Nothing in this report suggests otherwise. No official Redbelly statement on Quant or Overledger was found, so anything not in a public source is marked Unknown.

**How to read the labels.** **Confirmed** means a linked source says it. **Tested** means we ran the call ourselves on 19 or 20 October 2026, and the raw output is in `evidence/tests/`. **Analysis** means our reasoning from confirmed facts, not a statement by Redbelly, Tokeniser or Quant. **Unknown** means no source reviewed answers it.

## Short answer

| Question | Answer | Label |
|---|---|---|
| Could Overledger's Gateway reach Redbelly (read data, send signed transactions)? | Not shown so far. Redbelly has a public EVM RPC, and an Ankr endpoint for it, and Ankr is an approved Overledger provider. But Redbelly was not in Overledger's live network list, and our test registration of the Ankr endpoint was refused as an unsupported network. | Analysis |
| Can Redbelly join the Fusion Rollup (deposits, unified balances, cross-chain messages)? | Not listed today, as far as public sources show. | Analysis |
| Do Receptor credentials and Tokeniser rules travel with an asset to another chain? | No, not by themselves. | Analysis |
| Is there an announced agreement between Redbelly and Quant? | None found. | Confirmed |

## 1. Why now

**Confirmed.** On 24 September 2026 The Clearing House announced it had selected Quant to power its On-Chain Money Initiative, a network for banks to clear and settle tokenised deposit transactions [S1][S2]. Quant's technology is to provide the interoperability, orchestration and transaction-management layer, with connectivity to the RTP and CHIPS networks [S1]. The network is expected to open to participating institutions in the first half of 2027 [S1].

**Confirmed.** Both announcements say "Quant's technology". Neither names Overledger or lists any blockchain [S1][S2].

**Analysis.** The community question is natural, because Overledger is Quant's multi-chain platform [S3]. But the link between this initiative and Overledger's chain connectors is not stated in the announcements, so this report relies on Overledger's own documentation. Quant's site menu lists Overledger and Quant Fusion, among other links, but the release text does not say which of them the network will use [S2].

## 2. What Overledger is

**Confirmed.** Overledger is Quant's platform for building applications that span more than one blockchain, with one set of credentials and one API [S3]. It has three parts [S3]:

- **Gateway:** one authenticated entry point to many blockchain networks, so users do not run their own node connections.
- **Fusion Rollup:** a separate shared layer built on the OP Stack that anchors to several base chains at once.
- **Flow Applications:** multi-step business workflows that people, AI agents and services can all drive.

## 3. How chains connect today

**Confirmed.** Overledger connects chains through Connectors, in two forms [S4]:

- **Self-serve,** for public permissionless chains. A user registers a node and reaches the network through an API call, with no account-team involvement.
- **Managed engagement,** for permissioned, consortium or otherwise gated networks, and for public chains not yet self-serve (examples given: XRPL, Stellar, Bitcoin). This is a project with Quant's team.

**Confirmed.** Six chain families are self-serve today: EVM, Solana, Cosmos, SUI, Hedera and Aptos [S4]. A family qualifies if its nodes expose RPC or REST over HTTPS, the RPC needs no security factor beyond an API key, and node identity does not matter to other users [S4].

**Confirmed.** For a new network inside a supported family, the first node registration (`POST /nodes`) registers both the network and the node [S4]. A public node must come from one of seven approved providers (Alchemy, Infura, QuickNode, Chainstack, GetBlock, Blockdaemon, Ankr) [S4]. A private node can use any HTTPS address but is visible only to the account that added it [S4]. A health check runs at registration [S4].

**Confirmed.** For engagement networks, Quant asks for a short description of the network, the participants and the use case, and says it can normally onboard a chain that exposes RPC or REST over HTTP(S) with bearer or API-key authentication [S4].

**Confirmed.** Fusion is a separate path. Networks connected at its testnet launch were Ethereum Sepolia, Polygon Amoy and Quant's permissioned Besu testnet, and the live list comes from an API call [S5]. Fusion offers four actions: deposit, unify (merge several chains' copies of one asset into one balance), trigger (call a contract across chains) and withdraw or mint [S5]. Each connected chain hosts its own bridge and dispute contracts, one deployment per chain [S5]. Withdrawals are final only after a dispute window [S5].

**Confirmed.** Overledger's overview sorts networks into three kinds: public, public permissioned (consortium chains with public read access) and private permissioned [S23]. Its glossary says a public permissioned network is one where anyone can read but only allowlisted parties can write [S23]. The overview repeats the two ways to add a chain: self-serve for supported chain families, and a managed engagement with Quant's team for private or consortium networks and for new chain families [S23].

## 4. Redbelly facts that matter

**Confirmed.** Receptor is Redbelly's native identity and verifiable credential protocol. It facilitates network access and is built on the W3C verifiable credential model [S6]. Redbelly says issuers who provide network access are accredited [S6].

**Confirmed.** Proof by Query lets a user prove a fact, such as being over 18, to a verifier smart contract without revealing the underlying data on chain [S7]. In Redbelly's published flow, the business smart contract that verifies proofs is deployed on Redbelly, new issuer state is submitted to a state contract, and the credential's revocation status is checked before the proof is generated [S7].

**Confirmed.** Redbelly's developer portal says Receptor lets a developer program eligibility checks into smart contracts and dApps using verifiable credentials [S27]. It names two credential types: Proof by Query, which works on chain, and selective disclosure, which works off chain [S28]. The selective disclosure page says it can only be used off chain [S31]. Anyone can issue credentials with Receptor's issuer module, and some issuers are accredited by Redbelly governance to issue network access credentials [S28]. Each developer decides which issuers to trust for their own compliance needs [S28].

**Confirmed.** Redbelly's developer portal says every network participant must prove who they are before gaining access, and that Receptor facilitates this [S35]. It describes accredited issuers as a special class responsible for helping users and businesses through that process, and says all accredited issuers are listed in an on chain registry [S33]. The Eligibility SDK page says the SDK checks investor eligibility using Privado ID and the Iden3 zero-knowledge proof ecosystem, and its setup covers a backend verifier service [S36].

**Confirmed.** Redbelly's developer portal lists mainnet chain ID 151 and testnet chain ID 153, each with a public RPC address. For mainnet it also lists two third-party public RPC providers, Ankr and Uniblock, and says Uniblock needs an API key [S12].

**Tested.** A direct call to Redbelly's mainnet RPC on 19 October 2026 returned chain ID 0x97, which is 151, and reported the `net_version` method as not available on that endpoint [T1]. The same call on 20 October 2026 gave the same chain ID and the same `net_version` error, and `eth_blockNumber` answered with block 3,231,514, with no credential sent [T6]. A call to the testnet RPC address listed in the developer portal [S12] returned chain ID 0x99, which is 153, with the same `net_version` error [T7].

**Analysis.** The developer portal [S12], our own test [T1] and the TASK-16 playbook [S20] all give 151 for mainnet.

**Confirmed.** Redbelly says it is compatible with the EVM and can run contracts written for it, with EVM version Prague and Solidity version 0.8.30 [S13]. Before an account can write to the network, its user must claim an access credential from an accredited issuer and then enable the account through a network smart contract [S14]. The Eligibility Kit helps RWA issuers check investor eligibility with zero-knowledge proofs [S8], and a hook reads on-chain state to check whether an address has permission [S9].

**Confirmed.** Tokeniser is a Redbelly Network project. It says eligibility is programmed into every asset at protocol level and every transfer is checked against the asset's rules [S10]. Tokeniser's compliance page says identity, eligibility and limits are checked before any trade proceeds, and that a trade that fails a check does not proceed and is logged [S25]. Its technology page says Tokeniser runs on Redbelly Network and that eligibility is enforced at the point of transfer [S26]. Its secondary transfer page describes investors exiting between redemption windows by transferring a position to another eligible investor, with the fund's eligibility rules and limits applied automatically to each transfer [S37].

**Confirmed.** Redbelly can already be reached by a third-party bridge. In August 2025 Celer announced cBridge support: USDT, USDC, WBTC and ETH from Ethereum, LQDX from BNB Chain, and RBNT out to Ethereum and BNB Chain, initially as a pegged bridge [S11]. Redbelly's developer portal lists the same route and says RBNT bridges out from Redbelly to Ethereum and BNB Chain, not back [S30]. The portal also lists tokens that can be bridged between Redbelly and other chains through LayerZero, using Stargate, with the Oku bridge page as the interface [S29]. It lists a third route, Lucid Labs, powered by Polymer and LayerZero, for tokens that can be bridged between Redbelly and other chains [S34]. These routes are independent of Quant.

**Confirmed.** A community testnet bridge from the Task Board lets a user lock Sepolia ETH and receive wrapped WETH.rb on Redbelly testnet, and the page's own description calls it a 2-of-3 relayer scheme [S16]. A second community repository says that, as of July 2026, LayerZero, Axelar, Wormhole and Connext had no testnet deployment on Redbelly, and that LayerZero was live on Redbelly mainnet only. These are that author's findings and were not checked by us [S17]. Redbelly's own developer portal now lists a LayerZero route [S29]. The same repository describes its own bridge as a trusted-relayer design for testnet use, where whoever holds the relayer key can mint [S17].

## 5. Can Redbelly connect now?

| Route | Status | Label |
|---|---|---|
| Gateway, self-serve | Not listed today, our test registration was refused | Tested |
| Gateway, engagement | Documented path for gated chains, outcome unknown | Analysis |
| Fusion Rollup | Not listed today, as far as public sources show | Analysis |
| Third-party bridges (Celer, Router Nitro) | Live, but not an Overledger route | Confirmed |

**Tested.** On 19 October 2026 we read Overledger's live network list, which has 59 entries, and its Fusion list, which has 3 [T2]. Overledger's docs say the live list comes from this call [S4][S15]. No entry in either list mentions Redbelly, and none has chain ID 151 or 153 [T2]. Every network named in the list is a test network or a private network, including one permissioned Canton network, and none is named as a mainnet [T2]. The first two Fusion entries are Quant's own private network and Ethereum Sepolia [T2].

**Tested.** The live network entries label each network with `key`, `displayName` and `dltType`, while the docs describe `networkId`, `name` and `type` [T2][S4][S15]. The docs and the live service may differ in naming, so field names in this report follow the live output.

**Tested.** On 20 October 2026 we tried to register Ankr's Redbelly endpoint as a node in our own Overledger account. The request needs a `network` value and a `dlt` family [S22]. Without a network the call failed with "network : Required". With our guessed network name `redbelly-mainnet` it failed with "Unsupported network - check the RPC URL matches the selected network" [T3]. The Ankr endpoint itself answered chain ID 0x97 (151) when called directly [T4]. As a control, a node for Ethereum Sepolia, a network that is in the live list, was accepted and then deleted [T3]. So the request format worked, and the refusal came at the network step. Redbelly does not appear in the live network list [T2], so there was no listed name to copy. We then submitted six plausible names (Redbelly, Redbelly Mainnet, Redbelly Network, Redbelly Network Mainnet, and two testnet variants) on 20 October 2026. All six returned HTTP 400 with the same "Unsupported network" message, and no node was created [T5]. The identical message for every value means we cannot tell whether the name or the RPC check caused the refusal. This shows that none of these six values was accepted. It does not show that no accepted value exists.

**Tested.** The docs and the live service differ in four small ways. The reference page lists Bearer credentials and a 201 response for node registration [S22], but the same key was rejected as a Bearer token and accepted in the `X-API-Key` header, and the control registration returned HTTP 200 [T3]. The reference page also lists eight approved provider domains, adding drpc.live, while the Connectors page lists seven [S22][S4]. Which page is current is Unknown. Last, the reference page does not mark the network field as required, but a request without it was refused with HTTP 400 and a message saying the field is required [S22][T3].

**Tested.** On 20 October 2026 (20:30 UTC) we sent one GET request, with no credential, to the `/health` path of the Overledger service at `fusion-rollup.quant.dev`, which is the base address in Overledger's API reference [S15]. The reference lists that path as a liveness check, and its example response shows status "ok" with only `status`, `runtimeVersion` and `supportedSdkVersions` [S32]. The live service answered HTTP 200 with status "degraded", and its `checks` list showed `trackerPoller` as "stalled" and five other checks as ok or connected [T8]. The `checks` list is not in the reference example [S32][T8]. This is one call from one location. It describes that service on that date, says nothing about Redbelly, and we do not know what the stalled check means.

**Gateway, self-serve (Analysis).** Against Overledger's three tests [S4]: a Redbelly RPC over HTTPS exists [S12], and Redbelly is EVM compatible [S13], which is a supported self-serve family [S4]. Whether an endpoint works with an API key alone is Unknown, because Ankr's own terms were not reviewed. Ankr is on Overledger's approved provider list [S4] and lists a Redbelly mainnet endpoint [S12], so a public node registration looked possible in principle. We tried it and it was refused at the network step, as described above [T3]. Two doubts remain. Self-serve is described for public networks [S4], and writing to Redbelly needs an access credential [S14], so how Overledger would classify it is Unknown. And a private node serves only the account that registered it [S4].

**Gateway, engagement (Analysis).** This is the documented path for gated networks [S4]. Nothing in the docs excludes Redbelly, and nothing says it is accepted. The outcome would depend on Quant. Redbelly publishes public RPC addresses [S12], and one of them answered read calls without a credential [T6], but an account needs an access credential before it can write [S14]. That is close to what Overledger's overview calls a public permissioned network [S23]. No source says Quant would classify Redbelly this way, so which path applies is Unknown.

**Fusion Rollup (Analysis).** Redbelly is not in the testnet launch list, the docs describe no way for an outside network to be added, and connecting a chain needs bridge and dispute contracts deployed on it [S5]. The live Fusion list we read has no Redbelly entry [T2].

## 6. The work it would take

All of this is **Analysis**, in plain terms.

1. **Confirm the basics.** Get in writing whether read-only RPC access needs a credential, and whether Ankr's Redbelly endpoint works with an API key alone. Recheck Overledger's live network list, and ask Quant which network name a Redbelly node would be registered under, because our tests were refused at that step: one guessed name [T3] and six more [T5].
2. **Decide what "connect" means.** Reading data and sending signed transactions is the Gateway. Moving value and messages between chains is Fusion. They are different projects [S4][S5].
3. **Gateway work.** Register a node and pass the health check [S4]. Our attempts were refused with an "Unsupported network" message, and we cannot tell whether a health check was run [T3][T5]. If Redbelly's access rules do not fit self-serve, open an engagement with Quant [S4].
4. **Fusion work.** Deploy bridge and dispute contracts on Redbelly, have Fusion's services read Redbelly blocks and post state roots there, and list each allowed asset and sender in Fusion's allowlist contracts [S5]. Fusion sends transaction data to one permissioned chain and only state roots to the other connected chains [S5], so the Redbelly-side work is contracts plus state roots, not full transaction data. Fusion's token list is controlled by Quant's governance signers, and adding a token needs governance sign-off [S24]. Whether Redbelly's write-access credential affects Fusion's own services is Unknown [S5][S14]. Redbelly is not in Overledger's network list or its Fusion list [T2].
5. **Compliance design.** Decide which assets may leave Redbelly and how eligibility is checked at the other end (section 8). No source covers these three together: Fusion's asset mapping and sender allowlists live in its own contracts [S5]; Redbelly's eligibility proofs are checked by a verifier smart contract deployed on Redbelly, and the flow includes a revocation-status check of the credential [S7], and S5 does not describe Fusion calling them; and Tokeniser describes identity and eligibility as built into the protocol it runs on [S10], with nothing saying how that would apply to a copy of the asset elsewhere.
6. **Test.** Redbelly has a testnet with chain ID 153 [S12], and Fusion has a testnet with chain ID 73073 [S5].

**Unknown.** Time and cost. Quant gives about 2 days for a new chain-family checker and about 1 day per app [S4], but that is for a brand-new family, not for Redbelly, and no source gives a figure for Fusion.

## 7. What it could offer institutions

**Analysis, and only if a route existed.**

- **One integration point.** An institution already using Overledger [S3] could reach Redbelly-issued assets without a separate connection.
- **Cross-chain logic.** A Fusion contract could react to activity on several chains, including unified balances for assets that exist on more than one chain [S5].
- **Non-custodial design and a firewall.** Fusion's docs describe deposits and withdrawals signed by the user's own keys, with no relayer or custodian holding funds mid-flow, and a firewall that is locked down on mainnet [S5]. Whether the same would hold for Redbelly-issued assets is Unknown.
- **Identity-aware assets.** Redbelly would bring assets whose eligibility rules are built in [S6][S10]. Tokeniser, a product that runs on Redbelly, describes identity and eligibility as built into the protocol and says funds and companies can keep existing workflows for critical processes such as AML/KYC while they start tokenising [S10]. On the Overledger side, Quant describes a firewall that can filter requests by user identity, contract, function and parameter [S21]. These are two separate control layers, and no source says how they would work together.

**Limits.** No source says the Clearing House network will use the Gateway or Fusion, or connect any particular chain [S1][S2]. This section describes possibilities, not plans. The Tokeniser page we saved says nothing about moving tokens to other chains, so how Tokeniser assets would behave across chains is **Unknown** [S10].

## 8. Credentials and assets across chains

| Item | Where it works today | On another chain (Analysis) |
|---|---|---|
| Receptor credential | Held by the user, issued by an accredited issuer, proofs checked by contracts on Redbelly, revocation checked first [S6][S7]. Each contract chooses which issuers it trusts [S28]. Selective disclosure proofs work off chain only [S31] | No public source shows these proofs being verified on another chain |
| Tokeniser asset rules | Checked on every transfer on Redbelly [S10] | A pegged or wrapped copy follows the other chain's rules unless they are rebuilt there [S11] |
| Fusion allowlists | Per-asset token list and a sender list on the rollup; withdrawals only to chains where the user is allowlisted [S5]. The token list is set by Quant's governance signers, and sender lists by each contract's deployer [S24] | An allowlist is a list of addresses. It does not carry a credential's details or its revocation |

**Where compliance could break (Analysis).**

- **Rules left behind.** A copy of an asset on another chain may move freely even though the original could not.
- **Stale permission.** A Fusion allowlist is a list of addresses [S24], while a credential's revocation status is checked in Redbelly's published proof flow [S7]. So an entry could outlive the credential behind it.
- **Mixed balances.** Unifying several chains' copies into one balance [S5] could mix assets that follow different rules.
- **Dispute window.** Rollup withdrawals are not final straight away [S5], so a holder's status could change mid-transfer.
- **Two rule sets.** Overledger's firewall checks the Overledger user and the on-chain addresses bound to that user [S24]. Redbelly checks the access credential behind an account [S14]. No source says the two are linked.
- **Silent no-op.** On Fusion, a message from a sender who is not allowlisted does nothing on the rollup and does not fail on the connected chain [S24]. A transfer could look sent and never arrive.
- **Token approval by Quant.** A token must be on Fusion's token list, which Quant's governance signers control [S24]. A Redbelly asset could not be bridged this way unless Quant approves it.
- **Issuer trust is set per contract.** On Redbelly, each developer decides which issuers to trust [S28]. A contract on another chain would need its own choice. No source says it could reuse Redbelly's accredited issuers, which are listed in an on chain registry [S33].
- **Off chain proofs.** Selective disclosure is checked off chain by the verifier [S31], so it cannot be checked by a contract on another chain by itself.
- **Trust in the relayer.** The community testnet bridges for Redbelly move assets with relayers. The 2-of-3 bridge's own page says its signers can censor or delay mints and that it is not trustless or production-grade [S16]. In the single-relayer repository, whoever holds the relayer key can mint to any recipient and amount [S17]. In both, the relayers decide what is minted on the far side, so credential and eligibility checks would have to be added on top.
- **Extra steps and stuck transfers.** The TASK-16 playbook describes transfers to Ethereum that wait for a manual claim step, and deposits lost by sending on the wrong network [S20]. Any institutional route would need these cases handled before assets move.
- **Responsibility.** Tokeniser says products operate under the issuer's existing licensing [S10], and that offer, disclosure, onboarding and KYC stay with the issuer [S26]. A bridge does not change who is responsible, so each jurisdiction would need its own review.

**Confirmed.** Quant's own article of 12 February 2026 says Overledger has a firewall that filters requests by user identity, by smart contract, by contract function and by the values passed to the function, and that central banks and network operators can connect through it or bypass it [S21]. It also says every signature request is logged with who asked, who approved and which key was used [S21]. This is Quant describing its own product. It does not say the firewall can read a Redbelly credential, and it does not mention Fusion or Gateway.

**Confirmed.** Overledger's firewall documentation describes two layers [S24]. The connector layer runs inside the Gateway and checks the authenticated user on every network the Gateway reaches, and for a permissioned network the user must be on that network's allowlist [S24]. The Fusion layer runs on chain, in contracts on the rollup and on each connected chain's bridge, so the rules hold even if the Gateway is bypassed [S24]. Overledger keeps a link from each user to their authorised on-chain addresses, so a rule about a user becomes an address allowlist [S24]. Sender allowlists are managed per rollup contract by its deployer [S24]. The page does not mention Redbelly or Receptor, so how this firewall would apply to a Redbelly route is Unknown.

**Possible design directions (Analysis).** Keep restricted assets on Redbelly and move only unrestricted ones. Or keep allowlists updated from Redbelly's credential state. Or re-check eligibility when an asset comes back. None is confirmed to be supported by Overledger.

## 9. Not listed today, and unknown

**Unknown. Not listed today, as far as public sources show:** Redbelly as a Fusion network [S5]; registering Redbelly as a self-serve node today, since our attempt was refused as an unsupported network [T3]; Receptor proofs or Tokeniser's built-in identity and eligibility working on another chain without new work [S7][S10]; any claim that the Clearing House network will reach Redbelly [S1][S2].

**Unknown:** whether Ankr's Redbelly endpoint would pass Overledger's health check and API-key rule, since our registration stopped before that step [T3]; whether Quant could add a Redbelly network name on request; whether Quant's governance would approve a Redbelly asset for Fusion's token list [S24]; whether any third-party bridge route carries Redbelly's eligibility checks to the other chain [S29][S30][S34]; whether read-only RPC access needs a credential on every endpoint and method, since the one Redbelly mainnet endpoint we called answered three read-only calls without one on 20 October 2026 [T6]; whether a separate production network list exists, since the list we read showed no mainnets; whether Quant would treat Redbelly as self-serve or engagement [S4]; effort, time and cost; any Redbelly or Quant position on this; whether the Clearing House network will use the Gateway or Fusion.

## 10. What would change the answer

**Analysis.** The answers in this report rest on what public sources and our own tests showed between 19 and 21 October 2026. The table lists public signals a reader can check, and what the sources showed for each. They are checks, not predictions, and nothing here says any of them will happen.

| Signal a reader can check | Where to look | What we found |
|---|---|---|
| A Redbelly entry in Overledger's live network list | The network list call in Overledger's API reference [S15] | 59 entries, none for Redbelly, none with chain ID 151 or 153 [T2] |
| A Redbelly entry in Fusion's connected network list | The Fusion network list [S5] | 3 entries, none for Redbelly [T2] |
| A Redbelly node registration that is accepted | The node registration call [S22] | Seven network names tried, all refused as unsupported [T3][T5] |
| Overledger documentation that mentions Redbelly or Receptor | The Overledger overview, connectors, Fusion and firewall pages [S3][S4][S5][S23][S24] | None of these pages mention either |
| A named list of chains for the Clearing House network | The two announcements [S1][S2] | Neither lists any blockchain [S1][S2] |
| Documentation on carrying a credential check to another chain | Redbelly's proof flow and selective disclosure pages [S7][S31] | The verifier contract is deployed on Redbelly [S7], and selective disclosure works off chain only [S31] |
| A change to who controls Fusion's token list | The firewall documentation [S24] | Quant's governance signers control the list [S24] |
| An official Redbelly or Quant statement on this question | Their own official channels | None found, so this is Unknown |

**Analysis.** Which signal matters depends on the question. For the Gateway question, the network list and the node registration are the direct checks, because they are the steps our tests stopped at [T2][T3]. For the Fusion question, the Fusion network list and the contracts a connected chain must host are the checks [S5][T2]. For compliance, the first public sign would be documentation from Redbelly or Quant describing how a credential or eligibility check is carried to, or run again on, the other chain. None of the sources reviewed describes this [S7][S10][S24].

**Analysis.** A reader can repeat parts of this work. The calls to Redbelly's mainnet RPC and to the Overledger health path were sent without a credential [T6][T8]. The network list read and the node registration used an Overledger account key, which is not stored in any saved file [T2][T3]. Saved outputs and their SHA-256 hashes are in the evidence folder.

## 11. Method and limits

Sources were opened on 19, 20 and 21 October 2026; pages that block automated tools were copied by hand from a browser on 20 October. The Overledger pages reviewed show last-modified dates of June 2026, so they may have changed since. Two tests were run on 19 October 2026, a call to Redbelly's mainnet RPC [T1] and a read of Overledger's network lists [T2]. Six more were run on 20 October 2026, a node-registration test in Overledger [T3], a direct call to Ankr's Redbelly endpoint [T4], a six-name registration test [T5], a repeat call to Redbelly's mainnet RPC [T6], a call to Redbelly's testnet RPC [T7], and a call to the health path of the Overledger service [T8]. No Redbelly node was ever created. One control node on Ethereum Sepolia was created in the author's own account and deleted straight away [T3]. API keys were kept out of every saved file. Two resources from the task brief were read, the TASK-08 testnet bridge page and a second TASK-08 repository [S16][S17].

**Confirmed.** Redbelly Network's official X account posted that Wrapped RBNT is live on Ethereum Mainnet, gave an official contract address (`0xb45ffb51984d626ee758b336c61cf20990c6bf13`), and said the route is powered by Router Protocol's Nitro [S18]. Etherscan lists a token named Wrapped RBNT (WRBNT) at that address [S19]. This is a separate route from Quant and Overledger. Redbelly's developer portal lists Wrapped RBNT at the same Ethereum address, and also lists a Wrapped RBNT entry for Base under its Lucid Labs route [S34].

**Confirmed.** The TASK-16 recovery playbook, a Task Board deliverable, lists Reddex and Lucid Labs as official bridges between Ethereum and Redbelly, and says the wrapped RBNT contract Redbelly has officially announced is the Ethereum one, with no officially verified wrapped RBNT contract for BNB Chain or Base [S20]. These are the playbook's own statements. We checked only the Ethereum contract [S18][S19]. The portal's Base entry [S34] was not checked by us, so how it fits the playbook's statement about Base is Unknown. The wrapped RBNT post was read from a browser screenshot [S18] and its contract checked on Etherscan [S19]. The TASK-16 playbook was read from a PDF downloaded from the Task Board repository [S20], and its statements are used only as that document's own claims. Pages S2, S3, S4, S5 and S15 were read again on 20 October 2026 and saved as text copied from a browser. Sources are paraphrased, and the source list shows what each one supports.
