# Under concurrent requests, a wallet transfer can create money out of thin air.

If two transfers from the same wallet happen at the same time, the balance check passes for both and the total balance becomes negative — or both succeed when the combined amount exceeds the balance.
