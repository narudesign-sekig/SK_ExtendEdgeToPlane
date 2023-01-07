@warnings
@version 2.1
@name SK_ExtendEdgeToPlane

main
{
    selmode(DIRECT);
    n = pointcount();
    if (n != 5)
    {
        error("You need select 5 points");
    }

    editbegin();

    var x, y, z;

    po1 = pointinfo(points[1]);
    po2 = pointinfo(points[2]);
    po3 = pointinfo(points[3]);
    
    po4 = pointinfo(points[4]);
    po5 = pointinfo(points[5]);
    
    a = (po2.y - po1.y) * (po3.z - po1.z) - (po2.z - po1.z) * (po3.y - po1.y);
    b = (po2.z - po1.z) * (po3.x - po1.x) - (po2.x - po1.x) * (po3.z - po1.z);
    c = (po2.x - po1.x) * (po3.y - po1.y) - (po2.y - po1.y) * (po3.x - po1.x);
    d = - (a * po1.x + b * po1.y + c * po1.z);
    
    t = - (a * po4.x + b * po4.y + c * po4.z + d) / (a * (po5.x - po4.x) + b * (po5.y - po4.y) + c * (po5.z - po4.z));
    
    x = po4.x + t * (po5.x - po4.x);
    y = po4.y + t * (po5.y - po4.y);
    z = po4.z + t * (po5.z - po4.z);
    
    pointmove(points[5], x, y, z);

    editend();
}
