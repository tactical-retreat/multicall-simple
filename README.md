# multicall-simple

This is basically https://github.com/kkristof200/py_web3_multicall except flattened, simplified, dependencies removed, etc.

I don't like to pull in random web3 related deps into my projects out of paranoioa, and I particularly do not like dependencies
with dependencies.

So just copy paste this into your project instead. Usage is pretty straightforward, here's an example from my most recent project.

```python
def do_multicall(inputs: list, fn: Callable) -> list[Tuple]:
    # Splits a list of inputs into chunks of max size 500.
    # Then runs a function against each item in the input list, and passes that list to multicall.
    # Extracts the results  and returns a list of (input_argument, method_output)
    input_chunks = np.array_split(inputs, len(inputs) / 500)

    results = []
    for chunk in input_chunks:
        multicall_result = multicall.aggregate([fn(item) for item in chunk])
        for idx in range(len(chunk)):
            item = chunk[idx]
            result = multicall_result.results[idx].results[0]
            results.append((item, result))
    return results
    

# For every nft id,, gets the owner. 
# I used this in plague game where I wanted to know who owned every doctor/potion.
# 'client' is just a web3 wrapper around a connection, doctors is the nft contract.
nft_count = client.doctor_nft_count()
id_list = list(range(nft_count))
results = do_multicall(id_list, lambda nft_id: client.doctors.functions.ownerOf(int(nft_id)))

for nft_id, owner in results:
    nft_id = int(nft_id)
    owner = Web3.toChecksumAddress(owner)
```
