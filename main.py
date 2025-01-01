import os
from bip_utils import Bip39MnemonicGenerator, Bip39SeedGenerator, Bip44Coins, Bip44, base58, Bip44Changes
import pandas as pd

class BlockChainAccount:
    #默认生成10000个钱包地址，如需更改生成数量请更改num变量后面的参数
    def __init__(self, coin_type=Bip44Coins.ETHEREUM, password='', num=10000) -> None:
        self.coin_type = coin_type
        self.password = password
        self.num = num

    def get_address_pk(self):
        wallets = []
        for i in range(self.num):
            try:
                # 重新生成助记词
                self.mnemonic = Bip39MnemonicGenerator().FromWordsNumber(12)
                print(f"Generating wallet {i+1} with mnemonic: {self.mnemonic}")  # 添加日志打印

                seed_bytes = Bip39SeedGenerator(self.mnemonic).Generate(self.password)
                bip44_mst_ctx = Bip44.FromSeed(seed_bytes, self.coin_type)
                bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(i)
                bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
                priv_key_bytes = bip44_chg_ctx.PrivateKey().Raw().ToBytes()
                public_key_bytes = bip44_chg_ctx.PublicKey().RawCompressed().ToBytes()[1:]
                key_pair = priv_key_bytes + public_key_bytes
                wallet_info = {
                    'Wallet': f'Wallet-{i+1}',
                    'Mnemonic': self.mnemonic,  # 保存助记词
                    'Address': bip44_chg_ctx.PublicKey().ToAddress(),
                    'PriveteKey': base58.Base58Encoder.Encode(key_pair)
                }
                wallets.append(wallet_info)
            except Exception as e:
                print(f"Error generating wallet {i+1}: {e}")

        df = pd.DataFrame(wallets)
        output_dir = './data/output'
        os.makedirs(output_dir, exist_ok=True)  # 创建目录
        df.to_excel(f'{output_dir}/solana_wallets.xlsx', index=False)

coin_types = {
    Bip44Coins.SOLANA: 'solana',
}

for coin_type in coin_types.keys():
    chain_name = coin_types[coin_type]
    bca = BlockChainAccount(coin_type=coin_type)
    bca.get_address_pk()
