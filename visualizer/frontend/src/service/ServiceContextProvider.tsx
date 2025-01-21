import React, { createContext, PropsWithChildren, useContext } from "react";
import { GraphService, GraphServiceImpl } from "./GraphService";
import { DocService, DocServiceImpl } from "./DocService";
import { EntityService, EntityServiceImpl } from "./EntityService";
import { RelationService, RelationServiceImpl } from "./RelationService";

interface Services {
  graphService: GraphService;
  docService: DocService;
  entityService: EntityService;
  relationService: RelationService;
}

const ServiceContext = createContext<Services | undefined>(undefined);

export const ServiceContextProvider: React.FC<PropsWithChildren> = ({
  children,
}) => {
  const value: Services = {
    graphService: new GraphServiceImpl("http://localhost:5000"),
    docService: new DocServiceImpl("http://localhost:5000"),
    entityService: new EntityServiceImpl("http://localhost:5000"),
    relationService: new RelationServiceImpl("http://localhost:5000"),
  };

  return (
    <ServiceContext.Provider value={value}>{children}</ServiceContext.Provider>
  );
};

export const useServiceContext = (): Services => {
  const context = useContext(ServiceContext);
  if (!context) {
    throw new Error("useServiceContext must be used within a ServiceProvider");
  }
  return context;
};
