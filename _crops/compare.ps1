# Pixel compare: mock (frame1276.png) vs rendered page (render.png)
Add-Type -AssemblyName System.Drawing
Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;

public static class ImgDiff
{
    public static string Run(string pathA, string pathB, string outSide, string outDiff)
    {
        using (var a = new Bitmap(pathA))
        using (var b = new Bitmap(pathB))
        {
            int W = Math.Min(a.Width, b.Width);
            int H = Math.Min(a.Height, b.Height);
            var ra = a.LockBits(new Rectangle(0, 0, a.Width, a.Height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            var rb = b.LockBits(new Rectangle(0, 0, b.Width, b.Height), ImageLockMode.ReadOnly, PixelFormat.Format32bppArgb);
            var bytesA = new byte[ra.Stride * a.Height]; Marshal.Copy(ra.Scan0, bytesA, 0, bytesA.Length);
            var bytesB = new byte[rb.Stride * b.Height]; Marshal.Copy(rb.Scan0, bytesB, 0, bytesB.Length);
            a.UnlockBits(ra); b.UnlockBits(rb);

            var diff = new Bitmap(W, H);
            var rd = diff.LockBits(new Rectangle(0, 0, W, H), ImageLockMode.WriteOnly, PixelFormat.Format32bppArgb);
            var bytesD = new byte[rd.Stride * H];
            long total = 0;
            var rowCount = new int[H];
            var colCount = new int[W];
            for (int y = 0; y < H; y++)
            {
                int oa = y * ra.Stride, ob = y * rb.Stride, od = y * rd.Stride;
                for (int x = 0; x < W; x++)
                {
                    int ia = oa + x * 4, ib = ob + x * 4, id = od + x * 4;
                    int d = Math.Max(Math.Abs(bytesA[ia] - bytesB[ib]), Math.Max(Math.Abs(bytesA[ia + 1] - bytesB[ib + 1]), Math.Abs(bytesA[ia + 2] - bytesB[ib + 2])));
                    if (d > 32) { total++; rowCount[y]++; colCount[x]++; bytesD[id] = 0; bytesD[id + 1] = 0; bytesD[id + 2] = 255; bytesD[id + 3] = 255; }
                    else { bytesD[id] = 255; bytesD[id + 1] = 255; bytesD[id + 2] = 255; bytesD[id + 3] = 255; }
                }
            }
            diff.UnlockBits(rd);
            diff.Save(outDiff, ImageFormat.Png);

            using (var comp = new Bitmap(W * 2 + 16, H))
            using (var g = Graphics.FromImage(comp))
            {
                g.Clear(Color.White);
                g.DrawImage(a, 0, 0, W, H);
                g.DrawImage(b, W + 16, 0, W, H);
                comp.Save(outSide, ImageFormat.Png);
            }

            var sb = new StringBuilder();
            sb.AppendLine("total diff px = " + total + " of " + ((long)W * H));
            var rows = new List<KeyValuePair<int, int>>();
            for (int y = 0; y < H; y++) if (rowCount[y] > 0) rows.Add(new KeyValuePair<int, int>(y, rowCount[y]));
            rows.Sort(delegate (KeyValuePair<int, int> p1, KeyValuePair<int, int> p2) { return p2.Value.CompareTo(p1.Value); });
            sb.Append("top rows: ");
            for (int i = 0; i < Math.Min(18, rows.Count); i++) sb.Append("y" + rows[i].Key + "=" + rows[i].Value + " ");
            sb.AppendLine();
            var cols = new List<KeyValuePair<int, int>>();
            for (int x = 0; x < W; x++) if (colCount[x] > 0) cols.Add(new KeyValuePair<int, int>(x, colCount[x]));
            cols.Sort(delegate (KeyValuePair<int, int> p1, KeyValuePair<int, int> p2) { return p2.Value.CompareTo(p1.Value); });
            sb.Append("top cols: ");
            for (int i = 0; i < Math.Min(14, cols.Count); i++) sb.Append("x" + cols[i].Key + "=" + cols[i].Value + " ");
            return sb.ToString();
        }
    }
}
"@ -ReferencedAssemblies System.Drawing
Write-Output "mock vs render"
$res = [ImgDiff]::Run((Join-Path $PSScriptRoot 'frame1276.png'), (Join-Path $PSScriptRoot 'render.png'), (Join-Path $PSScriptRoot 'compare-side.png'), (Join-Path $PSScriptRoot 'diff.png'))
Write-Output $res
