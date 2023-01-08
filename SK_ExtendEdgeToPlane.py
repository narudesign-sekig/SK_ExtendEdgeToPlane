#! /usr/bin/env python
# -*- Mode: Python -*-
# -*- coding: ascii -*-

"""
Extend Edge To Plane
"""

import lwsdk, math

__author__      = "Makoto Sekiguchi"
__date__        = "Jan 8 2023"
__copyright__   = "Copyright (C) 2023 Makoto Sekiguchi"
__version__     = "1.0"
__maintainer__  = "Makoto Sekiguchi"
__status__      = "Release"
__lwver__       = "11"

class extendEdgeToPlane(lwsdk.ICommandSequence):
    def __init__(self, context):
        super(extendEdgeToPlane, self).__init__()
        
    def fast_edge_scan(self, edge_list, edge_id):
        edge_list.append(edge_id)
        return lwsdk.EDERR_NONE
        
    def fast_poly_scan(self, poly_list, poly_id):
        poly_list.append(poly_id)
        return lwsdk.EDERR_NONE
        
    def get_distance(self, p1, p2):
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)
        
    def process(self, mod_command):
        selectedPoly = []
        selectedEdge = []
        
        mc = mod_command
        
        mc.undoGroupBegin()
        meo = mc.editBegin(0, 0, lwsdk.OPSEL_DIRECT)
        
        edgeCount = meo.edgeCount(meo.state, lwsdk.OPLYR_FG, lwsdk.EDCOUNT_SELECT)
        polyCount = meo.polyCount(meo.state, lwsdk.OPLYR_FG, lwsdk.EDCOUNT_SELECT)
        
        if polyCount != 1:
            meo.done(meo.state, lwsdk.EDERR_NONE, 0)
            lwsdk.LWMessageFuncs().error("Please select 1 polygon", "")          
            return lwsdk.AFUNC_OK
            
        if edgeCount < 1:
            meo.done(meo.state, lwsdk.EDERR_NONE, 0)
            lwsdk.LWMessageFuncs().error("Please select 1 or more edges", "")          
            return lwsdk.AFUNC_OK
        
        eo_r = meo.fastPolyScan(meo.state, self.fast_poly_scan, (selectedPoly,), lwsdk.OPLYR_FG, 1)
        
        po = []
        po = meo.polyPoints(meo.state, selectedPoly[0])
        
        if len(po) < 3:
            meo.done(meo.state, lwsdk.EDERR_NONE, 0)
            lwsdk.LWMessageFuncs().error("Polygon must have at least 3 points", "")          
            return lwsdk.AFUNC_OK
        
        p1 = meo.pointPos(meo.state, po[0])
        p2 = meo.pointPos(meo.state, po[1])
        p3 = meo.pointPos(meo.state, po[2])
        
        a = (p2[1] - p1[1]) * (p3[2] - p1[2]) - (p2[2] - p1[2]) * (p3[1] - p1[1])
        b = (p2[2] - p1[2]) * (p3[0] - p1[0]) - (p2[0] - p1[0]) * (p3[2] - p1[2])
        c = (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])
        d = - (a * p1[0] + b * p1[1] + c * p1[2])
        
        eo_r = meo.fastEdgeScan(meo.state, self.fast_edge_scan, (selectedEdge,), lwsdk.OPLYR_FG, 1)
        
        for n in range(len(selectedEdge)):
            po4 = meo.edgePoint1(meo.state, selectedEdge[n])
            po5 = meo.edgePoint2(meo.state, selectedEdge[n])
            
            p4 = meo.pointPos(meo.state, po4)
            p5 = meo.pointPos(meo.state, po5)
            
            try:
                t = - (a * p4[0] + b * p4[1] + c * p4[2] + d) / (a * (p5[0] - p4[0]) + b * (p5[1] - p4[1]) + c * (p5[2] - p4[2]))
            except ZeroDivisionError:
                meo.done(meo.state, lwsdk.EDERR_NONE, 0)
                lwsdk.LWMessageFuncs().error("No intersection found.", "")          
                return lwsdk.AFUNC_OK
            
            x = p4[0] + t * (p5[0] - p4[0])
            y = p4[1] + t * (p5[1] - p4[1])
            z = p4[2] + t * (p5[2] - p4[2])
            pos = x, y, z
            
            # distP4 = math.sqrt((x - p4[0])**2 + (y - p4[1])**2 + (z - p4[2])**2)
            # distP5 = math.sqrt((x - p5[0])**2 + (y - p5[1])**2 + (z - p5[2])**2)
            distP4 = self.get_distance(pos, p4)
            distP5 = self.get_distance(pos, p5)
            
            if distP4 < distP5:
                meo.pntMove(meo.state, po4, pos)
            else:
                meo.pntMove(meo.state, po5, pos)
                
            
    # for (i = 0; i < floor((n - 3)/2); i++)
    # {
        # po4 = pointinfo(points[4 + i * 2]);
        # po5 = pointinfo(points[5 + i * 2]);
        
        # t = - (a * po4.x + b * po4.y + c * po4.z + d) / (a * (po5.x - po4.x) + b * (po5.y - po4.y) + c * (po5.z - po4.z));
        
        # x = po4.x + t * (po5.x - po4.x);
        # y = po4.y + t * (po5.y - po4.y);
        # z = po4.z + t * (po5.z - po4.z);
        
        # pointmove(points[5 + i * 2], x, y, z);
    # }
    
    
        # move up +0.1
        # for n in range(len(po)):
            # posBefore = meo.pointPos(meo.state, po[n])
            # posAfter = posBefore[0], posBefore[1] + 0.1, posBefore[2]
            # meo.pntMove(meo.state, po[n], posAfter)
            
            
        # eo_r = meo.fastEdgeScan(meo.state,self.fast_edge_scan, (edge,), lwsdk.OPLYR_FG, 1)
        
        # for n in range(2):
            # planePnts.append(meo.edgePoint1(meo.state, edge[n]))
            # planePnts.append(meo.edgePoint2(meo.state, edge[n]))
        
        # po1 = meo.edgePoint1(meo.state, edge[0])
        # po2 = meo.edgePoint2(meo.state, edge[0])
        # pos = meo.pointPos(meo.state, po2)
        # meo.pntMove(meo.state, po1, pos)
            
        meo.done(meo.state, lwsdk.EDERR_NONE, 0)
        mc.undoGroupEnd()
        
        return lwsdk.AFUNC_OK

ServerTagInfo = [
    ("SK_ExtendEdgeToPlane", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH ),
    ("SK_ExtendEdgeToPlane", lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH )
]
ServerRecord = {
    lwsdk.CommandSequenceFactory("SK_ExtendEdgeToPlane", extendEdgeToPlane) : ServerTagInfo
}