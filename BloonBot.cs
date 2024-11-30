using MelonLoader;
using BTD_Mod_Helper;
using BloonBot;
using System;
using System.Net.Sockets;
using System.Text;
using Il2CppAssets.Scripts.Simulation.Towers.Weapons.Behaviors;
using Il2CppAssets.Scripts.Unity;
using Il2CppAssets.Scripts.Unity.UI_New.InGame;
using Il2CppAssets.Scripts.Models;
using Il2CppAssets.Scripts.Data.Behaviors.Projectiles;
using Il2CppAssets.Scripts.Models.Map;
using Il2CppAssets.Scripts.Simulation;
using System.Collections.Generic;


[assembly: MelonInfo(typeof(BloonBot.BloonBot), ModHelperData.Name, ModHelperData.Version, ModHelperData.RepoOwner)]
[assembly: MelonGame("Ninja Kiwi", "BloonsTD6")]

namespace BloonBot;

public class BloonBot : BloonsTD6Mod
{

    public override void OnApplicationStart()
    {
        ModHelper.Msg<BloonBot>("BloonBot loaded!");
    }


    //send message to python
    private static void ToPython(string message)
    {
        string serverIp = "127.0.0.1";
        int serverPort = 764;

        try
        {
            using (TcpClient client = new TcpClient(serverIp, serverPort))
            using (NetworkStream stream = client.GetStream())
            {
                byte[] data = Encoding.UTF8.GetBytes(message);
                stream.Write(data, 0, data.Length);
                stream.Close();
            }
        }

        catch (Exception ex)
        {
            ModHelper.Msg<BloonBot>($"Error sending data to server: {ex.Message}");
        }
    }


    //get round, lives, and cash
    static void GetInfo(int offset = 0)
    {
        int round = InGame.instance.bridge.GetCurrentRound() + 1 + offset;
        double cash = InGame.instance.bridge.GetCash();
        float lives = InGame.instance.bridge.GetHealth();

        ToPython("round:"+round);
        ToPython("cash:"+cash);
        ToPython("lives:"+lives);
    }


    //get ONLY cash
    static void GetMoney()
    {
        double cash = InGame.instance.bridge.GetCash();
        ToPython("cash:"+cash);
    }


    //times to use
    public override void OnRestart()
    {
        base.OnRestart();
        GetInfo();
    }


    public override void OnRoundEnd()
    {
        base.OnRoundEnd();
        GetInfo(offset:1);
    }


    public override void OnInGameLoaded(InGame inGame)
    {
        base.OnInGameLoaded(inGame);
        GetInfo();
    }


    public override void OnCashRemoved(double amount, Simulation.CashType from, int cashIndex, Simulation.CashSource source)
    {
        base.OnCashRemoved(amount, from, cashIndex, source);
        GetMoney();
    }
}