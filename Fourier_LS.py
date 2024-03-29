
#----------------------------------------------------------------------
def Fourier_LS(head,tail,surf,Lt,inorm,g):
    print('Calculating Particle Fields...')
    time=len(Lt)
    N=head.shape[1]
    L=Lt[:,None]
    ln=np.sum((tail-head)**2,axis=2)**.5       # lipid length              time * N
    D_z=abs(tail[:,:,2]-head[:,:,2])           # lipid z                   time * N
    if inorm==0: norms=ln                      # normalization factors     time * N
    elif inorm==1: norms=D_z
    ns=(tail-head)/norms[:,:,None]             # lipid directors           time * N * 3
    hN =surf[:,:,2]-np.mean(surf[:,:,2])
    z_c=np.mean(tail[:,:,2],axis=1)            # midplane                  time
    alphas=(head[:,:,2].T>z_c).T               # leaflet index             time * N
    ns*=(alphas[:,:,None]*2-1)
    s1=surf[:,:,0]+L/2
    s2=surf[:,:,1]+L/2

    print('Least-Squares Fourier Analysis...')
    q,Qx,Qy,Q2,sorter,ignorer=Wavenumbers(g,np.mean(Lt))
    this=np.where(Q2<3000.)
    hq2t=np.zeros((2,time,len(this[0])))
    nqlls=np.zeros((time,len(this[0])))
    nqllc=np.zeros((time,len(this[0])))
    nqll2t=np.zeros((time,len(this[0])))
    nqLs=np.zeros((time,len(this[0])))
    nqLc=np.zeros((time,len(this[0])))
    nqL2t=np.zeros((time,len(this[0])))
    start = tm.time()
    for t in range(time):
        if t%1000==0: print(t)
        L=Lt[t]
        q,Qx,Qy,Q2,sorter,ignorer=Wavenumbers(g,L)
        Qx=Qx[this[0]]
        Qy=Qy[this[0]]
        Q2=Q2[this[0]]
        Q=np.sqrt(Q2)
        qx=Qx*q[0]
        qy=Qy*q[0]

        for layer in [True,False]: #TODO make a function of what's in this for loop
            pick=np.where(alphas[t] == layer)[0]
            h_layer=hN[t,pick]
            x_layer=s1[t,pick] #TODO Instead of L**2/4 at the and, maybe add L/2 here correctly
            y_layer=s2[t,pick]
            temp=qx[np.newaxis,:]*x_layer[:,np.newaxis]+qy[np.newaxis,:]*y_layer[:,np.newaxis]
            temp=temp[:,this[0]]
            basis= np.concatenate((np.sin(temp),np.cos(temp)), axis=1)
            lin_fy= np.linalg.lstsq(basis,h_layer,rcond=None)
            lin_fy=lin_fy[0]*1
            lin_fy[0]=0
            hqs=lin_fy[:int(len(lin_fy)/2)]
            hqc=lin_fy[int(len(lin_fy)/2):]
            hq2t[layer*1,t]=hqc**2+hqs**2
    #     pick=np.where((D_z[t]/ln[t]>0.565)*(alphas[t] == layer))[0]
        pick=np.where(D_z[t]/ln[t]>0.565)[0]
        nxN=ns[t,pick,0]*(alphas[t,pick]*2-1)
        nyN=ns[t,pick,1]*(alphas[t,pick]*2-1)
        x_layer  = s1[t,pick]
        y_layer  = s2[t,pick]
        temp=qx[np.newaxis,:]*x_layer[:,np.newaxis]+qy[np.newaxis,:]*y_layer[:,np.newaxis]
        temp=temp[:,this[0]]
        basis= np.concatenate((np.sin(temp),np.cos(temp)), axis=1)
        lin_fy= np.linalg.lstsq(basis,nxN,rcond=None)
        lin_fy=lin_fy[0]*1
        lin_fy[0]=0
        nxqs=lin_fy[:int(len(lin_fy)/2)]
        nxqc=lin_fy[:int(len(lin_fy)/2)]
        lin_fy= np.linalg.lstsq(basis,nyN,rcond=None)
        lin_fy=lin_fy[0]*1
        lin_fy[0]=0
        nyqs=lin_fy[:int(len(lin_fy)/2)]
        nyqc=lin_fy[:int(len(lin_fy)/2)]

        nqlls[t]=(nxqs*Qx+nyqs*Qy)/Q
        nqllc[t]=(nxqc*Qx+nyqc*Qy)/Q
        nqLs[t] =(nxqs*Qy-nyqs*Qx)/Q
        nqLc[t] =(nxqc*Qy-nyqc*Qx)/Q

    #         nqll2t[layer*1,t]=nqlls[t]**2+nqllc[t]**2
    #         nqL2t[layer*1,t]=nqLs[t]**2+nqLc[t]**2
        nqll2t[t]=nqlls[t]**2+nqllc[t]**2
        nqL2t[t]=nqLs[t]**2+nqLc[t]**2
    hq2t  =(hq2t[0]+hq2t[1])/2
    end = tm.time()
    print(str(round(   (end - start)/time*1000,2   ))+' s/1000 frames')
    # hq2t  =hq2t.reshape(2*time,len(this[0]))
    # nqll2t  =(nqll2t[0]+nqll2t[1])/2
    # # nqL2t  =(nqL2t[0]+nqL2t[1])/2
    # q= 2*np.pi/np.mean(Lt)*(np.linspace(0,M,M+1)[:-1])
    # Qx=(q[:,np.newaxis]+q[np.newaxis,:]*0)
    # Qy=(q[:,np.newaxis]*0+q[np.newaxis,:])
    # Q =(q[:,np.newaxis]**2+q[np.newaxis,:]**2)**.5
    q,Qx,Qy,Q2,sorter,ignorer=Wavenumbers(g,np.mean(Lt))
    Qx=Qx[this[0]]
    Qy=Qy[this[0]]
    Q2= Q2[this[0]]
    Q=np.sqrt(Q2)
    hq2t=hq2t[:,Q.argsort()]
    nqll2t=nqll2t[:,Q.argsort()]
    nqL2t=nqL2t[:,Q.argsort()]
    Qx=Qx[Q.argsort()]
    Qy=Qy[Q.argsort()]
    Q=Q[Q.argsort()]
    hq2t=hq2t[:,:]*np.mean(Lt)**2/4#*L*np.pi
    nqll2t=nqll2t[:,:]*np.mean(Lt)**2/4#*L*np.pi
    nqL2t=nqL2t[:,:]*np.mean(Lt)**2/4#*L*np.pi
    q=Q*q[0]
    qx=Qx*q[0]
    qy=Qy*q[0]
    return hq2t,nqll2t,nqL2t,q,qx,qy
#----------------------------------------------------------------------
