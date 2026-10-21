# Community summary

**In a few paragraphs.** The Clearing House picked Quant on 24 September 2026 to power a bank network for tokenised deposits, expected in the first half of 2027 [S1]. People asked whether Redbelly could plug into Quant's Overledger platform. This research looks at what public sources say. It is not a statement about any partnership, and none has been announced.

Overledger has two parts that matter here. The Gateway connects apps to many chains, and the Fusion Rollup moves value and messages between chains [S3]. The Gateway has a self-serve route for public chains and a project route for gated ones [S4]. Whether Redbelly fits either is not confirmed. Fusion's docs describe no way for an outside chain to join, so Redbelly is not listed on that route today, as far as public sources show [S5].

Receptor credentials and Tokeniser rules are enforced on Redbelly [S7][S10]. Moving an asset to another chain does not carry those checks along by itself. Keeping compliance intact would need extra design work. Redbelly has a public EVM RPC and an Ankr endpoint, and Ankr is on Overledger's approved provider list [S4][S12], but Redbelly was not in Overledger's live network list when checked, and that list showed test networks only [T2]. When we tried to register Ankr's Redbelly endpoint in Overledger, the request was refused as an unsupported network [T3]. Many details are unknown, including how Quant would classify Redbelly.

**X thread (each post is under 280 characters).**

1/ The Clearing House chose Quant for its On-Chain Money Initiative, a tokenised deposit network for banks, expected in H1 2027. Can Redbelly connect to Quant's Overledger? We read the public sources. Feasibility only, no partnership announced. [S1]

2/ Overledger has two routes. The Gateway links apps to many chains, self-serve for public ones and by project for gated ones. Fusion Rollup moves value across chains. Redbelly is not confirmed on either. [S3][S4]

3/ Fusion's docs list Sepolia, Polygon Amoy and a Besu testnet at launch and describe no way for outside chains to join. Not listed today, as far as public sources show. [S5]

4/ Compliance is the hard part. Receptor credentials and Tokeniser rules are enforced on Redbelly. A copy of an asset elsewhere would not carry them by itself. [S7][S10]

5/ Tested: Redbelly is absent from Overledger's live network list, and registering Ankr's Redbelly endpoint was refused as an unsupported network. Unknown: how Quant would classify Redbelly, effort and timing. [T2][T3] Full report is in the DAO's TASK-29 research.
