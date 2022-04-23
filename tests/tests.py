import brownie
from brownie import interface, Contract, accounts
import pytest
import time 

def sneakyAdminPrint(gov, token): 
    balanceBefore  = token.balanceOf(gov)
    token.grantRole(token.MINTER_BURNER_ROLE(), gov, {'from' : gov })
    token.revokeRole(token.DEFAULT_ADMIN_ROLE(), gov, {'from' : gov})
    mintAmount = 10000
    token.mint(gov, mintAmount, {'from' : gov}) 
    balanceAfter  = token.balanceOf(gov)
    assert (balanceAfter - balanceBefore) == mintAmount 
    print("users got rekt...")

def test_admin_mint(gov, h20Token, iceToken, steamToken, controller) : 
    print("Admin is priiiiiiinting")
    sneakyAdminPrint(gov, h20Token)
    sneakyAdminPrint(gov, iceToken)
    sneakyAdminPrint(gov, steamToken)
   

def test_iceBurnError(gov, user, iceToken) : 
    print("Gonna try to send all my ICE....")
    iceToken.grantRole(iceToken.MINTER_BURNER_ROLE(), gov, {'from' : gov })
    mintAmount = (2**256 - 1) / 10000
    userBalanceBefore = iceToken.balanceOf(user)
    iceToken.mint(gov, mintAmount, {'from' : gov}) 
    with brownie.reverts():
        iceToken.transfer(user, mintAmount)

def sendHalfTokensToUser(gov, user, h20Token, iceToken, steamToken) : 
    h20TokenBal = h20Token.balanceOf(gov)
    steamTokenBal = steamToken.balanceOf(gov)
    h20Token.transfer(user, h20TokenBal*0.5)
    steamToken.transfer(user, steamTokenBal*0.5)


def test_transferAndClaimBetweenUsers(gov, user ,accounts, h20Token, iceToken, steamToken, controller, chain) :
    h20TokenBalGov = h20Token.balanceOf(gov)
    h20TokenBalUser = h20Token.balanceOf(user)
    controller.claimRewards(True, True, {'from' : gov})
    controller.claimRewards(True, True, {'from' : user})
    steamTokenBal = steamToken.balanceOf(gov)
    #iceToken.transfer(iceTokenBal, user, {'from' : gov})
    steamToken.transfer(user, steamTokenBal, {'from' : gov})
    controller.claimRewards(True, True, {'from' : gov})
    controller.claimRewards(True, True, {'from' : user})
    chain.mine(10)
    chain.sleep(10000)

    steamTokenRewardsUser = steamToken.claimableReward(user)
    steamToken.transfer(gov, steamTokenBal, {'from' : user})
    steamTokenRewardsGov = steamToken.claimableReward(gov)
    print("Pending Rewards : " + str(steamTokenRewardsUser))
    print("Pending Rewards : " + str(steamTokenRewardsGov))


def arb_swap_functions_STM(gov, h20Token, iceToken, steamToken, controller) : 
    controller.claimRewards(True, True)
    h20TokenBal = h20Token.balanceOf(gov)
    iceTokenBal = iceToken.balanceOf(gov)
    steamTokenBal = steamToken.balanceOf(gov)

    swapAmt = steamTokenBal*0.9
    amtOut = controller.previewSwapSTMForH2O(swapAmt)
    controller.swapSTMForH2O(swapAmt, {'from' : gov})
    assert steamToken.balanceOf(gov) == steamTokenBal - swapAmt
    assert h20Token.balanceOf(gov) == h20TokenBal + amtOut
    controller.claimRewards(True, True)

    controller.swapH2OForSTM(amtOut, {'from' : gov})
    assert steamToken.balanceOf(gov) > steamTokenBal
    assert h20Token.balanceOf(gov) >= h20TokenBal
    assert iceToken.balanceOf(gov) >= iceTokenBal



def test_arb_swap_functions_STM(gov, h20Token, iceToken, steamToken, controller) : 
    n_loops = 100
    h20TokenBal = h20Token.balanceOf(gov)
    iceTokenBal = iceToken.balanceOf(gov)
    steamTokenBal = steamToken.balanceOf(gov)

    

    for i in range(n_loops) : 
        arb_swap_functions_STM(gov, h20Token, iceToken, steamToken, controller)

    h20TokenBalAfter = h20Token.balanceOf(gov)
    iceTokenBalAfter = iceToken.balanceOf(gov)
    steamTokenBalAfter = steamToken.balanceOf(gov)    

    print("H20 Profit : " + str(h20TokenBalAfter / h20TokenBal))
    print("ICE Profit : " + str(iceTokenBalAfter / iceTokenBal))
    print("STM Profit : " + str(steamTokenBalAfter / steamTokenBal))




def arb_swap_functions_H2O(gov, h20Token, iceToken, steamToken, controller) : 
    controller.claimRewards(True, True)
    h20TokenBal = h20Token.balanceOf(gov)
    iceTokenBal = iceToken.balanceOf(gov)
    steamTokenBal = steamToken.balanceOf(gov)

    #swap Triangle 
    swapAmt = h20TokenBal*0.9
    amtOut = controller.previewSwapH2OForSTM(swapAmt)
    controller.swapH2OForSTM(swapAmt, {'from' : gov})
    assert h20Token.balanceOf(gov) == h20TokenBal - swapAmt
    assert steamToken.balanceOf(gov) == steamTokenBal + amtOut
    controller.claimRewards(True, True)

    controller.swapSTMForH2O(amtOut, {'from' : gov})
    assert steamToken.balanceOf(gov) >= steamTokenBal
    assert h20Token.balanceOf(gov) > h20TokenBal
    assert iceToken.balanceOf(gov) >= iceTokenBal


def test_arb_swap_functions_H20(gov, h20Token, iceToken, steamToken, controller) : 
    n_loops = 100
    h20TokenBal = h20Token.balanceOf(gov)
    iceTokenBal = iceToken.balanceOf(gov)
    steamTokenBal = steamToken.balanceOf(gov)
    for i in range(n_loops) : 
        arb_swap_functions_H2O(gov, h20Token, iceToken, steamToken, controller)

    h20TokenBalAfter = h20Token.balanceOf(gov)
    iceTokenBalAfter = iceToken.balanceOf(gov)
    steamTokenBalAfter = steamToken.balanceOf(gov)    

    print("H20 Profit : " + str(h20TokenBalAfter / h20TokenBal))
    print("ICE Profit : " + str(iceTokenBalAfter / iceTokenBal))
    print("STM Profit : " + str(steamTokenBalAfter / steamTokenBal))
