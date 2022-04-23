import pytest
from brownie import config
from brownie import Contract
from brownie import interface, project


@pytest.fixture
def gov(accounts) : 
    yield accounts[0]

@pytest.fixture
def user(accounts) : 
    yield accounts[1]


@pytest.fixture
def h20Token(H2OToken, gov) : 
    token = H2OToken.deploy(gov, {'from' : gov})
    yield token 


@pytest.fixture
def iceToken(IceToken, gov) : 
    token = IceToken.deploy(gov, {'from' : gov})
    yield token

@pytest.fixture
def steamToken(SteamToken, gov) : 
    token = SteamToken.deploy(gov, {'from' : gov})
    yield token

@pytest.fixture
def controller(h20Token, iceToken, steamToken, Controller, gov) : 
    controller = Controller.deploy(iceToken, h20Token, steamToken, {'from' : gov})
    h20Token.grantRole(h20Token.DEFAULT_ADMIN_ROLE(), controller, {'from' : gov})
    iceToken.grantRole(iceToken.DEFAULT_ADMIN_ROLE(), controller, {'from' : gov})
    steamToken.grantRole(steamToken.DEFAULT_ADMIN_ROLE(), controller, {'from' : gov})

    controller.initTokenRoles({'from' : gov})
    yield controller 


@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass